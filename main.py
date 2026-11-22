from utilidades.gestor_logs import configurar_logger
from modelos.cliente import Cliente
from modelos.servicio import Servicio, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from modelos.reserva import Reserva
from excepciones.errores_sistema import ErrorSoftwareFJ


class SistemaSoftwareFJ:
    def __init__(self):
        self.logger = configurar_logger("logs/eventos_software_fj.log")
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        self.logger.info("=== INICIO DE EJECUCIÓN DEL SISTEMA SOFTWARE FJ ===")

    def registrar_cliente(self, id_c: str, nombre: str, doc: str, correo: str, tel: str) -> Cliente | None:
        nuevo_cliente = None
        try:
            nuevo_cliente = Cliente(id_c, nombre, doc, correo, tel)
        except ErrorSoftwareFJ as err:
            self.logger.error(
                f"Fallo al registrar cliente ({id_c}): {err} | Causa raíz: {repr(err.__cause__)}"
            )
        else:
            self.clientes.append(nuevo_cliente)
            self.logger.info(f"Cliente registrado exitosamente: {nuevo_cliente.obtener_resumen()}")
        finally:
            self.logger.info(f"Finalizado intento de registro para ID cliente: {id_c}")
        return nuevo_cliente

    def registrar_servicio(self, servicio_fn, etiqueta: str) -> Servicio | None:
        try:
            servicio = servicio_fn()
        except ErrorSoftwareFJ as err:
            self.logger.error(
                f"Fallo al crear servicio [{etiqueta}]: {err} | Causa encadenada: {repr(err.__cause__)}"
            )
            return None
        else:
            self.servicios.append(servicio)
            self.logger.info(f"Servicio habilitado: {servicio.describir_servicio()}")
            return servicio

    def gestionar_reserva(
        self,
        id_r: str,
        cliente: Cliente,
        servicio: Servicio,
        horas: int,
        descuento: float = 0.0,
        accion: str = "PROCESAR",
    ) -> Reserva | None:
        reserva = None
        try:
            reserva = Reserva(id_r, cliente, servicio, horas, descuento)
            reserva.confirmar()
            if accion == "PROCESAR":
                comprobante = reserva.procesar()
                self.logger.info(f"Reserva procesada con éxito -> {comprobante}")
            elif accion == "CANCELAR":
                reserva.cancelar("Cambio de agenda del cliente")
                self.logger.warning(f"Reserva cancelada correctamente: {reserva.obtener_resumen()}")
        except ErrorSoftwareFJ as err:
            detalle_causa = f" -> Encadenado desde: {err.__cause__}" if err.__cause__ else ""
            self.logger.error(f"Error en operación de reserva ({id_r}): {err}{detalle_causa}")
        else:
            self.reservas.append(reserva)
        finally:
            self.logger.info(f"Cierre de transacción de reserva [{id_r}].")
        return reserva


def ejecutar_simulacion():
    sistema = SistemaSoftwareFJ()

    print("\n--- FASE 1: REGISTRO DE CLIENTES (VÁLIDOS E INVÁLIDOS) ---")
    c1 = sistema.registrar_cliente("CLI-001", "Laura Martínez", "1020304050", "laura@empresa.com", "3105551234")
    c2 = sistema.registrar_cliente("CLI-002", "Carlos Gómez", "80123456", "cgomez@tech.co", "3009876543")
    sistema.registrar_cliente("CLI-003", "Pedro Pérez", "123", "correo-sin-arroba", "3112223344")
    sistema.registrar_cliente("CLI-004", "", "1098765432", "vacio@dominio.com", "3150009988")

    print("\n--- FASE 2: CREACIÓN DE SERVICIOS ESPECIALIZADOS (POLIMORFISMO) ---")
    s_sala = sistema.registrar_servicio(
        lambda: ReservaSala("SRV-101", "Sala Innovación", 80000.0, capacidad_personas=12, tiene_videoconferencia=True),
        "Sala Innovación",
    )
    s_equipo = sistema.registrar_servicio(
        lambda: AlquilerEquipo("SRV-201", "Workstation Dell Precision", 45000.0, "Workstation", stock_disponible=1),
        "Workstation Dell",
    )
    s_asesoria = sistema.registrar_servicio(
        lambda: AsesoriaEspecializada("SRV-301", "Auditoría Ciberseguridad", 120000.0, "Seguridad Cloud", "Arquitecto"),
        "Auditoría Ciberseguridad",
    )
    sistema.registrar_servicio(
        lambda: ReservaSala("SRV-999", "Sala Defectuosa", -50000.0, capacidad_personas=5),
        "Sala Tarifa Negativa",
    )

    print("\n--- FASE 3: GESTIÓN DE RESERVAS Y EXCEPCIONES AVANZADAS ---")
    r1 = sistema.gestionar_reserva("RES-001", c1, s_sala, horas=4, descuento=10.0, accion="PROCESAR")
    sistema.gestionar_reserva("RES-002", c2, s_equipo, horas=5, descuento=0.0, accion="PROCESAR")
    sistema.gestionar_reserva("RES-003", c1, s_equipo, horas=3, accion="PROCESAR")

    try:
        if r1 is not None:
            r1.cancelar("Intento tardío de cancelación")
    except ErrorSoftwareFJ as err:
        sistema.logger.error(f"Bloqueo de regla de negocio verificado: {err}")

    print("\n--- RESUMEN POLIMÓRFICO DEL PORTAFOLIO DE SERVICIOS ---")
    for srv in sistema.servicios:
        print(" ->", srv.describir_servicio())

    sistema.logger.info(
        f"=== FIN DE SIMULACIÓN | Clientes activos: {len(sistema.clientes)} | "
        f"Servicios: {len(sistema.servicios)} | Reservas exitosas: {len(sistema.reservas)} ==="
    )


if __name__ == "__main__":
    ejecutar_simulacion()
