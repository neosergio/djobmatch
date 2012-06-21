from django.contrib import admin
from joboffers.models import Pais, Departamento, Provincia, Distrito
from joboffers.models import Persona, Sede, Empresa, ContactoEmpresa, Sector
from joboffers.models import Formacion, Especialidad, EstadoEspecialidad, RequerimientoEspecialidad
from joboffers.models import Software, EstadoSoftware, RequerimientoSoftware
from joboffers.models import TipoContrato, Oferta, Area, Cargo, Funcion
from joboffers.models import CorreoEnviarOferta
from joboffers.models import Idioma, EstadoIdioma, RequerimientoIdioma
from joboffers.models import Postulante


admin.site.register(Pais)
admin.site.register(Departamento)
admin.site.register(Provincia)
admin.site.register(Distrito)
admin.site.register(Persona)
admin.site.register(Sede)
admin.site.register(Empresa)
admin.site.register(ContactoEmpresa)
admin.site.register(Sector)
admin.site.register(Formacion)
admin.site.register(Especialidad)
admin.site.register(EstadoEspecialidad)
admin.site.register(RequerimientoEspecialidad)
admin.site.register(Software)
admin.site.register(EstadoSoftware)
admin.site.register(RequerimientoSoftware)
admin.site.register(TipoContrato)
admin.site.register(Oferta)
admin.site.register(Area)
admin.site.register(Cargo)
admin.site.register(CorreoEnviarOferta)
admin.site.register(Idioma)
admin.site.register(EstadoIdioma)
admin.site.register(RequerimientoIdioma)
admin.site.register(Funcion)
admin.site.register(Postulante)
