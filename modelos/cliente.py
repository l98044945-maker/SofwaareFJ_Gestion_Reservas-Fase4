import re
from modelos.entidad import EntidadSistema
from excepciones.errores_sistema import DatosInvalidosError, ParametroFaltanteError


class Cliente(EntidadSistema):
    def __init__(self, id_cliente: str, nombre: str, documento: str, correo: str, telefono: str):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        self.__historial_reservas: list[str] = []
        self.validar_integridad()

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError("El nombre del cliente no puede estar vacío.")
        nombre_limpio = str(valor).strip()
        if len(nombre_limpio) < 3 or any(char.isdigit() for char in nombre_limpio):
            raise DatosInvalidosError(
                f"Nombre inválido '{valor}': debe tener al menos 3 caracteres y no incluir números."
            )
        self.__nombre = nombre_limpio

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError("El documento de identidad es obligatorio.")
        doc_limpio = str(valor).strip()
        if not doc_limpio.isdigit() or not (6 <= len(doc_limpio) <= 12):
            raise DatosInvalidosError(
                f"Documento inválido '{valor}': debe ser numérico entre 6 y 12 dígitos."
            )
        self.__documento = doc_limpio

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError("El correo electrónico es obligatorio.")
        correo_limpio = str(valor).strip().lower()
        patron_email = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(patron_email, correo_limpio):
            raise DatosInvalidosError(f"Formato de correo electrónico inválido: '{valor}'.")
        self.__correo = correo_limpio

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError("El número de teléfono es obligatorio.")
        tel_limpio = str(valor).strip()
        if not tel_limpio.isdigit() or not (7 <= len(tel_limpio) <= 15):
            raise DatosInvalidosError(
                f"Teléfono inválido '{valor}': debe contener entre 7 y 15 dígitos."
            )
        self.__telefono = tel_limpio

    @property
    def historial_reservas(self) -> list[str]:
        return list(self.__historial_reservas)

    def registrar_reserva_en_historial(self, id_reserva: str) -> None:
        if not id_reserva:
            raise ParametroFaltanteError("El ID de reserva a registrar no puede ser vacío.")
        self.__historial_reservas.append(id_reserva)

    def validar_integridad(self) -> bool:
        return all([self.__nombre, self.__documento, self.__correo, self.__telefono])

    def obtener_resumen(self) -> str:
        return (
            f"Cliente [{self.id_entidad}] | Nombre: {self.__nombre} | "
            f"Doc: {self.__documento} | Email: {self.__correo} | "
            f"Reservas asociadas: {len(self.__historial_reservas)}"
        )
