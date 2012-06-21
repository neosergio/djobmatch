#encoding:utf-8
from django.forms import ModelForm
from django.contrib.auth.models import User
from joboffers.models import Pais, Departamento, Provincia, Distrito
from joboffers.models import Persona, Sede, Empresa, ContactoEmpresa, Sector
from joboffers.models import Formacion, Especialidad, EstadoEspecialidad, RequerimientoEspecialidad
from joboffers.models import Software, EstadoSoftware, RequerimientoSoftware
from joboffers.models import TipoContrato, Oferta, Area, Cargo, Funcion
from joboffers.models import CorreoEnviarOferta
from joboffers.models import Idioma, EstadoIdioma, RequerimientoIdioma
from joboffers.models import Postulante
from django.contrib.formtools.wizard import FormWizard
from django.http import HttpResponseRedirect

class Oferta_formulario(ModelForm):
	class Meta:
		model = Oferta
		exclude = ('enviado','contacto_empresa')

class RequerimientoEspecialidad_formulario(ModelForm):
	class Meta:
		model = RequerimientoEspecialidad
		exclude = ('oferta',)

class RequerimientoSoftware_formulario(ModelForm):
	class Meta:
		model = RequerimientoSoftware
		exclude = ('oferta',)

class RequerimientoIdioma_formulario(ModelForm):
	class Meta:
		model = RequerimientoIdioma
		exclude = ('oferta',)

class Funcion_formulario(ModelForm):
	class Meta:
		model= Funcion
		exclude = ('oferta',)

class CorreoEnviarOferta_formulario(ModelForm):
	class Meta:
		model = CorreoEnviarOferta
		exclude = ('oferta',)

class PostulanteFormulario(ModelForm):
	class Meta:
		model = Postulante
		exclude = ('persona',)


class amarrado(FormWizard):
	def done(self, request, form_list):
		datos = {}
		for form in form_list:
			datos.update(form.cleaned_data)
		
		#Guardar la oferta
		contacto_empresa = datos['contacto_empresa']
		sede = datos['sede']
		fecha = datos['fecha']
		dias = datos['dias']
		titulo = datos['titulo']
		vacantes = datos['vacantes']
		descripcion = datos['descripcion']
		area = datos['area']
		cargo = datos['cargo']
		tipo_contrato = datos['tipo_contrato']
		salario = datos['salario']
		beneficio = datos['beneficio']
		requerimiento = datos['requerimiento']
		indicacion = datos['indicacion']
		oferta = Oferta(contacto_empresa=contacto_empresa, sede=sede, fecha=fecha, dias=dias, titulo=titulo, vacantes=vacantes, descripcion=descripcion, area=area, cargo=cargo, tipo_contrato=tipo_contrato, salario=salario, beneficio=beneficio, requerimiento=requerimiento, indicacion=indicacion)
		oferta.save()
		
		#Guardar la funcion
		oferta = Oferta.objects.latest('id')
		descripcion_funcion = datos['descripcion_funcion']
		funcion = Funcion(oferta=oferta, descripcion_funcion=descripcion_funcion)
		funcion.save()
		
		#Guardar el correo enviar oferta
		correo = datos['correo']
		tipo = datos['tipo']
		correoenviar = CorreoEnviarOferta(oferta=oferta, correo=correo, tipo=tipo)
		correoenviar.save()		
		
		return HttpResponseRedirect('/')
