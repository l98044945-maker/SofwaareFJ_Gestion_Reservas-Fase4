from abc import ABC, abstractmethod
from datetime import datetime
from excepciones.errores_sistema import ParametroFaltanteError, DatosInvalidosError


class EntidadSistema(ABC):
    def __init__(self, id_entidad: str):
        if id_entidad is None or not str(id_entidad).strip():
            raise ParametroFaltanteError("El identificador de la entidad es obligatorio.")
        if len(str(id_entidad).strip()) < 3:
            raise DatosInvalidosError(
                f"El ID '{id_entidad}' es demasiado corto; debe tener al menos 3 caracteres."
            )
        self.__id_entidad = str(id_entidad).strip().upper()
        self.__fecha_creacion = datetime.now()

    @property
    def id_entidad(self) -> str:
        return self.__id_entidad

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    @abstractmethod
    def validar_integridad(self) -> bool:
        pass

    @abstractmethod
    def obtener_resumen(self) -> str:
        pass

    def __str__(self) -> str:
        return self.obtener_resumen()
