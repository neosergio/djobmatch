#encoding:utf-8
from django.contrib.auth.models import User
from django.db import models
import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

class Pais(models.Model):
	codigo = models.CharField(max_length=3, verbose_name='Código', primary_key=True)
	nombre = models.CharField(max_length=100,verbose_name='País')
	
	def __unicode__(self):
		return self.nombre

class Departamento(models.Model):
	codigo = models.CharField(max_length=2, verbose_name='Código', primary_key=True)
	nombre = models.CharField(max_length=100,verbose_name='Departamento')
	pais = models.ForeignKey(Pais)
	
	def __unicode__(self):
		return self.nombre

class Provincia(models.Model):
	codigo = models.CharField(max_length=4, verbose_name='Código', primary_key=True)
	nombre = models.CharField(max_length=100,verbose_name='Provincia')
	departamento = models.ForeignKey(Departamento)
	
	def __unicode__(self):
		return self.nombre

class Distrito(models.Model):
	codigo = models.CharField(max_length=6, verbose_name='Código', primary_key=True)
	nombre = models.CharField(max_length=100,verbose_name='Distrito')
	provincia = models.ForeignKey(Provincia)

	def __unicode__(self):
		return self.nombre

class Sector(models.Model):
	nombre = models.CharField(max_length=100,verbose_name='Sector')
		
	def __unicode__(self):
		return self.nombre

class Empresa(models.Model):
	ruc = models.CharField(max_length=11,verbose_name='R.U.C')
	razon_social = models.CharField(max_length=100,verbose_name='Razón Social')
	nombre_comercial = models.CharField(max_length=255,verbose_name='Nombre comercial')
	sector = models.ForeignKey(Sector)

	def __unicode__(self):
		return self.nombre_comercial

class Sede(models.Model):
	empresa = models.ForeignKey(Empresa)
	descripcion = models.TextField(verbose_name='Descripción')
	direccion = models.CharField(max_length=255, verbose_name='Dirección')
	distrito = models.ForeignKey(Distrito)

	def __unicode__(self):
		return self.empresa.nombre_comercial + " " + self.direccion

class Persona(models.Model):
	codigo = models.CharField(max_length=10, verbose_name='Código', primary_key=True)
	apellidos = models.CharField(max_length=255)
	nombres = models.CharField(max_length=255)
	genero = models.CharField(max_length=1, choices=(('M','Masculino'),('F','Femenino')))
	usuario = models.OneToOneField(User)

	def __unicode__(self):
		return self.apellidos + " " + self.nombres

class ContactoEmpresa(models.Model):
	persona = models.ForeignKey(Persona)
	sede = models.ForeignKey(Sede)
	cargo = models.CharField(max_length=100, verbose_name='Cargo en la empresa')
	
	def __unicode__(self):
		return self.cargo

class Formacion(models.Model):
	nombre = models.CharField(max_length=100, verbose_name='Formación')
	
	def __unicode__(self):
		return self.nombre
		
class Especialidad(models.Model):
	nombre = models.CharField(max_length=100)
	formacion = models.ForeignKey(Formacion)
	
	def __unicode__(self):
		return self.nombre
	
class EstadoEspecialidad(models.Model):
	nombre = models.CharField(max_length=100)
	
	def __unicode__(self):
		return self.nombre
		
class Software(models.Model):
	nombre = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.nombre
		
class EstadoSoftware(models.Model):
	nombre = models.CharField(max_length=100)
	
	def __unicode__(self):
		return self.nombre
	
class Area(models.Model):
	nombre = models.CharField(max_length=100)
	
	def __unicode__(self):
		return self.nombre

class Cargo(models.Model):
	nombre = models.CharField(max_length=100)
	
	def __unicode__(self):
		return self.nombre

class TipoContrato(models.Model):
	nombre = models.CharField(max_length=100)
	
	def __unicode__(self):
		return self.nombre

class Oferta(models.Model):
	contacto_empresa = models.ForeignKey(ContactoEmpresa)
	sede = models.ForeignKey(Sede)
	fecha = models.DateField(default=datetime.date.today)
	dias = models.PositiveIntegerField(verbose_name='Días de duración de la oferta')
	titulo = models.CharField(max_length=255,verbose_name='Título')
	vacantes = models.PositiveIntegerField(verbose_name='Número de vacantes',default=1)
	descripcion = models.TextField(verbose_name='Descripción')
	area = models.ForeignKey(Area)
	cargo = models.ForeignKey(Cargo)
	tipo_contrato = models.ForeignKey(TipoContrato)
	salario = models.DecimalField(max_digits=7,decimal_places=2,blank=True,null=True)
	beneficio = models.TextField(blank=True,null=True)
	requerimiento = models.TextField(blank=True,null=True)
	indicacion = models.TextField(blank=True,null=True)
	enviado = models.BooleanField(default=False)
	
	def __unicode__(self):
		return self.titulo

class Funcion(models.Model):
	oferta = models.ForeignKey(Oferta)
	descripcion_funcion = models.CharField(max_length=200, verbose_name='Descripción')
	
	def __unicode__(self):
		return self.descripcion_funcion

class Idioma(models.Model):
	nombre = models.CharField(max_length=100)
	
	def __unicode__(self):
		return self.nombre

class EstadoIdioma(models.Model):
	nombre = models.CharField(max_length=100)
	
	def __unicode__(self):
		return self.nombre

class RequerimientoIdioma(models.Model):
	idioma = models.ForeignKey(Idioma)
	lectura = models.OneToOneField(EstadoIdioma, related_name='nivel_lectura')
	escritura = models.OneToOneField(EstadoIdioma, related_name='nivel_escritura')
	conversacion = models.OneToOneField(EstadoIdioma, related_name='nivel_conversacion')
	oferta = models.ForeignKey(Oferta)

	def __unicode__(self):
		return self.lectura.nombre + " " + self.escritura.nombre + " " + self.conversacion.nombre
	
class RequerimientoEspecialidad(models.Model):
	oferta = models.ForeignKey(Oferta)
	especialidad_elegida = models.ForeignKey(Especialidad)
	estado = models.ForeignKey(EstadoEspecialidad)
	condicion = models.CharField(max_length=100, verbose_name='Condición')
	anos_experiencia = models.PositiveIntegerField(verbose_name='Años de experiencia')

	def __unicode__(self):
		return self.estado.nombre

class RequerimientoSoftware(models.Model):
	oferta = models.ForeignKey(Oferta)
	software = models.ForeignKey(Software)
	estado_software = models.ForeignKey(EstadoSoftware)
	
	def __unicode__(self):
		return self.oferta.titulo + " " + self.software.nombre + " " + self.estado_software.nombre

class CorreoEnviarOferta(models.Model):
	oferta = models.ForeignKey(Oferta)
	correo = models.EmailField(verbose_name='Correo electrónico')
	
	def __unicode__(self):
		return self.correo

class Postulante(models.Model):
	persona = models.ForeignKey(Persona)
	dni = models.CharField(max_length=8, verbose_name='DNI')
	fnacimiento = models.DateField(verbose_name='Fecha de nacimiento')
	foto = models.ImageField(verbose_name='Fotografía', upload_to='postulante')
	estadocivil = models.CharField(max_length=1, choices=(('S','Soltero'),('C','Cásado'),('D','Divorciado'),('V','Viudo')))
	presentacion = models.TextField(verbose_name='Presentación')
	
	def get_absolute_url(self):
		#return reverse('postulante-detail', kwargs={'pk':self.pk})
		return HttpResponseRedirect('/')

	def __unicode__(self):
		return self.dni
	
