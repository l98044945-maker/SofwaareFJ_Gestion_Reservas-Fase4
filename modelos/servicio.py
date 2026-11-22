from abc import abstractmethod
from modelos.entidad import EntidadSistema
from excepciones.errores_sistema import (
    DatosInvalidosError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
    CalculoInconsistenteError,
)


class Servicio(EntidadSistema):
    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__(id_servicio)
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.__disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        self.__nombre = str(valor).strip()

    @property
    def tarifa_base(self) -> float:
        return self.__tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: float) -> None:
        try:
            tarifa = float(valor)
        except (TypeError, ValueError) as exc:
            raise DatosInvalidosError(f"La tarifa base '{valor}' debe ser numérica.") from exc
        if tarifa <= 0:
            raise DatosInvalidosError(
                f"La tarifa base ({tarifa}) debe ser mayor que cero."
            )
        self.__tarifa_base = tarifa

    @property
    def disponible(self) -> bool:
        return self.__disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        self.__disponible = bool(estado)

    @abstractmethod
    def validar_parametros_operacion(self, duracion_horas: int) -> None:
        pass

    @abstractmethod
    def calcular_costo_base(self, duracion_horas: int) -> float:
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        pass

    def calcular_costo_total(
        self,
        duracion_horas: int,
        impuesto_iva: float = 0.19,
        descuento_porcentaje: float = 0.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        if not self.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' ({self.id_entidad}) no está disponible actualmente."
            )
        self.validar_parametros_operacion(duracion_horas)

        if impuesto_iva < 0 or impuesto_iva > 1:
            raise CalculoInconsistenteError(
                f"Porcentaje de IVA inválido ({impuesto_iva}); debe estar entre 0.0 y 1.0."
            )
        if descuento_porcentaje < 0 or descuento_porcentaje >= 100:
            raise CalculoInconsistenteError(
                f"Descuento inválido ({descuento_porcentaje}%); debe estar entre 0 y 99.9."
            )
        if recargo_adicional < 0:
            raise CalculoInconsistenteError("El recargo adicional no puede ser negativo.")

        subtotal = self.calcular_costo_base(duracion_horas)
        valor_con_descuento = subtotal * (1 - (descuento_porcentaje / 100.0))
        total = (valor_con_descuento * (1 + impuesto_iva)) + recargo_adicional

        if total <= 0:
            raise CalculoInconsistenteError(
                f"El cálculo total arrojó un valor inconsistente: {total}."
            )
        return round(total, 2)

    def validar_integridad(self) -> bool:
        return bool(self.__nombre) and self.__tarifa_base > 0

    def obtener_resumen(self) -> str:
        return self.describir_servicio()


class ReservaSala(Servicio):
    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        capacidad_personas: int,
        tiene_videoconferencia: bool = True,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not isinstance(capacidad_personas, int) or capacidad_personas <= 0:
            raise DatosInvalidosError(
                f"La capacidad de la sala ({capacidad_personas}) debe ser un entero positivo."
            )
        self.__capacidad_personas = capacidad_personas
        self.__tiene_videoconferencia = bool(tiene_videoconferencia)

    @property
    def capacidad_personas(self) -> int:
        return self.__capacidad_personas

    def validar_parametros_operacion(self, duracion_horas: int) -> None:
        if not isinstance(duracion_horas, int) or duracion_horas < 1 or duracion_horas > 12:
            raise DatosInvalidosError(
                f"Duración inválida para sala ({duracion_horas}h): permitido entre 1 y 12 horas."
            )

    def calcular_costo_base(self, duracion_horas: int) -> float:
        self.validar_parametros_operacion(duracion_horas)
        costo = self.tarifa_base * duracion_horas
        if self.__tiene_videoconferencia:
            costo *= 1.10
        return round(costo, 2)

    def describir_servicio(self) -> str:
        equipo_av = "Con Videoconferencia" if self.__tiene_videoconferencia else "Estándar"
        estado = "Disponible" if self.disponible else "No Disponible"
        return (
            f"Sala [{self.id_entidad}] '{self.nombre}' | Aforo: {self.__capacidad_personas} pers. | "
            f"{equipo_av} | Tarifa/h: ${self.tarifa_base:,.2f} | Estado: {estado}"
        )


class AlquilerEquipo(Servicio):
    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        categoria_hardware: str,
        stock_disponible: int,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not categoria_hardware or not str(categoria_hardware).strip():
            raise ParametroFaltanteError("La categoría de hardware es obligatoria.")
        if not isinstance(stock_disponible, int) or stock_disponible < 0:
            raise DatosInvalidosError(
                f"El stock disponible ({stock_disponible}) no puede ser negativo."
            )
        self.__categoria_hardware = str(categoria_hardware).strip()
        self.__stock_disponible = stock_disponible
        if self.__stock_disponible == 0:
            self.disponible = False

    @property
    def stock_disponible(self) -> int:
        return self.__stock_disponible

    def descontar_unidad(self) -> None:
        if self.__stock_disponible <= 0:
            raise ServicioNoDisponibleError(
                f"No hay unidades en stock para el equipo '{self.nombre}'."
            )
        self.__stock_disponible -= 1
        if self.__stock_disponible == 0:
            self.disponible = False

    def reponer_unidad(self) -> None:
        self.__stock_disponible += 1
        if self.__stock_disponible > 0:
            self.disponible = True

    def validar_parametros_operacion(self, duracion_horas: int) -> None:
        if self.__stock_disponible <= 0:
            raise ServicioNoDisponibleError(
                f"Stock agotado para el equipo '{self.nombre}' ({self.id_entidad})."
            )
        if not isinstance(duracion_horas, int) or duracion_horas < 2 or duracion_horas > 72:
            raise DatosInvalidosError(
                f"Duración inválida para alquiler ({duracion_horas}h): permitido entre 2 y 72 horas."
            )

    def calcular_costo_base(self, duracion_horas: int) -> float:
        self.validar_parametros_operacion(duracion_horas)
        seguro_equipo = 15000.0
        return round((self.tarifa_base * duracion_horas) + seguro_equipo, 2)

    def describir_servicio(self) -> str:
        return (
            f"Equipo [{self.id_entidad}] '{self.nombre}' | Categoría: {self.__categoria_hardware} | "
            f"Stock: {self.__stock_disponible} uds | Tarifa/h: ${self.tarifa_base:,.2f}"
        )


class AsesoriaEspecializada(Servicio):
    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        especialidad: str,
        nivel_seniority: str = "Senior",
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not especialidad or not str(especialidad).strip():
            raise ParametroFaltanteError("La especialidad de la asesoría es obligatoria.")
        niveles_validos = {"Junior", "Semi-Senior", "Senior", "Arquitecto"}
        if nivel_seniority not in niveles_validos:
            raise DatosInvalidosError(
                f"Nivel '{nivel_seniority}' no válido. Opciones: {niveles_validos}."
            )
        self.__especialidad = str(especialidad).strip()
        self.__nivel_seniority = nivel_seniority

    def validar_parametros_operacion(self, duracion_horas: int) -> None:
        if not isinstance(duracion_horas, int) or duracion_horas < 1 or duracion_horas > 8:
            raise DatosInvalidosError(
                f"Duración inválida para asesoría ({duracion_horas}h): permitido entre 1 y 8 horas."
            )

    def calcular_costo_base(self, duracion_horas: int) -> float:
        self.validar_parametros_operacion(duracion_horas)
        factores = {
            "Junior": 1.0,
            "Semi-Senior": 1.2,
            "Senior": 1.4,
            "Arquitecto": 1.75,
        }
        multiplicador = factores[self.__nivel_seniority]
        return round(self.tarifa_base * duracion_horas * multiplicador, 2)

    def describir_servicio(self) -> str:
        return (
            f"Asesoría [{self.id_entidad}] '{self.nombre}' | Área: {self.__especialidad} | "
            f"Nivel: {self.__nivel_seniority} | Tarifa base/h: ${self.tarifa_base:,.2f}"
        )
