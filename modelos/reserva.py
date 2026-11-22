from modelos.entidad import EntidadSistema
from modelos.cliente import Cliente
from modelos.servicio import Servicio, AlquilerEquipo
from excepciones.errores_sistema import (
    DatosInvalidosError,
    ParametroFaltanteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)


class Reserva(EntidadSistema):
    ESTADO_PENDIENTE = "PENDIENTE"
    ESTADO_CONFIRMADA = "CONFIRMADA"
    ESTADO_PROCESADA = "PROCESADA"
    ESTADO_CANCELADA = "CANCELADA"

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: int,
        descuento_aplicado: float = 0.0,
    ):
        super().__init__(id_reserva)

        if cliente is None or not isinstance(cliente, Cliente):
            raise ParametroFaltanteError("Se requiere una instancia válida de Cliente.")
        if servicio is None or not isinstance(servicio, Servicio):
            raise ParametroFaltanteError("Se requiere una instancia válida de Servicio.")

        if not isinstance(duracion_horas, int) or duracion_horas <= 0:
            raise ReservaInvalidaError(
                f"La duración de la reserva ({duracion_horas}) debe ser un entero mayor a 0."
            )

        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion_horas = duracion_horas
        self.__descuento_aplicado = descuento_aplicado
        self.__estado = self.ESTADO_PENDIENTE
        self.__costo_total = 0.0

        try:
            self.__costo_total = self.__servicio.calcular_costo_total(
                duracion_horas=self.__duracion_horas,
                descuento_porcentaje=self.__descuento_aplicado,
            )
        except (DatosInvalidosError, ServicioNoDisponibleError) as exc:
            raise ReservaInvalidaError(
                f"No fue posible inicializar la reserva '{self.id_entidad}' para el servicio "
                f"'{servicio.nombre}': {exc.mensaje}"
            ) from exc

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def costo_total(self) -> float:
        return self.__costo_total

    def confirmar(self) -> None:
        if self.__estado != self.ESTADO_PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva '{self.id_entidad}' porque está en estado '{self.__estado}'."
            )
        if not self.__servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.__servicio.nombre}' dejó de estar disponible."
            )
        if isinstance(self.__servicio, AlquilerEquipo):
            self.__servicio.descontar_unidad()

        self.__estado = self.ESTADO_CONFIRMADA
        self.__cliente.registrar_reserva_en_historial(self.id_entidad)

    def procesar(self) -> str:
        if self.__estado != self.ESTADO_CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"Solo se pueden procesar reservas CONFIRMADAS. Estado actual: '{self.__estado}'."
            )
        self.__estado = self.ESTADO_PROCESADA
        return (
            f"Comprobante Reserva {self.id_entidad} | Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} | Duración: {self.__duracion_horas}h | "
            f"Total Facturado (IVA incl.): ${self.__costo_total:,.2f}"
        )

    def cancelar(self, motivo: str = "Solicitud del cliente") -> None:
        if self.__estado == self.ESTADO_PROCESADA:
            raise OperacionNoPermitidaError(
                f"La reserva '{self.id_entidad}' ya fue PROCESADA y no admite cancelación."
            )
        if self.__estado == self.ESTADO_CANCELADA:
            raise OperacionNoPermitidaError(
                f"La reserva '{self.id_entidad}' ya se encuentra CANCELADA."
            )
        if self.__estado == self.ESTADO_CONFIRMADA and isinstance(self.__servicio, AlquilerEquipo):
            self.__servicio.reponer_unidad()

        self.__estado = self.ESTADO_CANCELADA

    def validar_integridad(self) -> bool:
        return (
            self.__cliente is not None
            and self.__servicio is not None
            and self.__costo_total > 0
        )

    def obtener_resumen(self) -> str:
        return (
            f"Reserva [{self.id_entidad}] | Estado: {self.__estado} | "
            f"Cliente: {self.__cliente.nombre} | Servicio: {self.__servicio.nombre} | "
            f"Horas: {self.__duracion_horas} | Total: ${self.__costo_total:,.2f}"
        )
