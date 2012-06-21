#encoding:utf-8
from joboffers.models import Pais, Departamento, Provincia, Distrito
from joboffers.models import Persona, Sede, Empresa, ContactoEmpresa, Sector
from joboffers.models import Formacion, Especialidad, EstadoEspecialidad, RequerimientoEspecialidad
from joboffers.models import Software, EstadoSoftware, RequerimientoSoftware
from joboffers.models import TipoContrato, Oferta, Area, Cargo, Funcion
from joboffers.models import CorreoEnviarOferta
from joboffers.models import Idioma, EstadoIdioma, RequerimientoIdioma
from joboffers.models import Postulante
from joboffers.forms import Oferta_formulario, Funcion_formulario, CorreoEnviarOferta_formulario
from joboffers.forms import RequerimientoEspecialidad_formulario
from joboffers.forms import RequerimientoSoftware_formulario
from joboffers.forms import RequerimientoIdioma_formulario
from joboffers.forms import PostulanteFormulario
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.core.mail import EmailMessage
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

login_url_path = '/ingreso'

def inicio(request):
	usuario = request.user
	if usuario.is_anonymous():
		return render_to_response('inicio.html', context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/administrar')

def ingresoadmin(request):
	if not request.user.is_anonymous():
		print "no es anonimo"
		return HttpResponseRedirect('/administrar')
	if request.method == 'POST':
		form = AuthenticationForm(request.POST)
		if form.is_valid:
			usuario = request.POST['username']
			clave = request.POST['password']
			acceso = authenticate(username=usuario,password=clave)
			if acceso is not None:
				if acceso.is_active:
					login(request, acceso)
					return HttpResponseRedirect('/administrar')
				else: 
					return render_to_response('noactivo.html')
			else:
				return render_to_response('nousuario.html')
	else:
		form = AuthenticationForm(auto_id=True)
	return render_to_response('ingresoadmin.html',{'form':form},context_instance=RequestContext(request))

def no_es_postulante(user):
	if user:
		return user.groups.filter(name='postulantes').count() == 0
	return False

@login_required(login_url=login_url_path)
def administrar(request):
	usuario = request.user
	no_postulante = usuario.groups.filter(name='postulantes').count() == 0
	no_ofertante = usuario.groups.filter(name='ofertantes').count() == 0
	if not no_postulante:
		postulante = True
		ofertante = False
	if not no_ofertante:
		postulante = False
		ofertante = True
	if not no_postulante and not no_ofertante:
		postulante = True
		ofertante = True
	return render_to_response('administrar.html',{'postulante':postulante,'ofertante':ofertante},context_instance=RequestContext(request))

@login_required(login_url=login_url_path)
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid:
            form.save()
            return HttpResponseRedirect('/admin')
    else:
        form = UserCreationForm()
    return render_to_ressponse('registro.html',{'form':form},context_instance=RequestContext(request))


@login_required(login_url=login_url_path)
def nueva_oferta(request):
    if request.method == 'POST':
        form = Oferta_formulario(request.POST)
        if form.is_valid():
            form.save()
            ultimo = Oferta.objects.latest('id')
            redireccion = '/oferta/' + str(ultimo.id)
            return HttpResponseRedirect(redireccion)
    else:
        form = Oferta_formulario(auto_id=True)
    return render_to_response('ofertaform.html',{'form':form},context_instance=RequestContext(request)) 

@login_required(login_url=login_url_path)
def nuevo_requerimientoespecialidad(request, id_oferta):
	if request.method == 'POST':
		form = RequerimientoEspecialidad_formulario(request.POST)
		if form.is_valid():
			oferta_consulta = Oferta.objects.get(pk=id_oferta)
			estado_oferta = oferta_consulta.enviado
			if not estado_oferta:
				especialidad_form = form.cleaned_data['especialidad']
				estado_form = form.cleaned_data['estado']
				condicion_form = form.cleaned_data['condicion']
				experiencia_form = form.cleaned_data['anos_experiencia']
				requerimiento = RequerimientoEspecialidad(oferta=oferta_consulta, especialidad=especialidad_form, estado=estado_form, condicion=condicion_form, anos_experiencia=experiencia_form)
				requerimiento.save()
				redireccion = '/oferta/' + str(oferta_consulta.id)
				return HttpResponseRedirect(redireccion)
			else:
				return render_to_response('ofertaenviada.html')
	else:
		form = RequerimientoEspecialidad_formulario(auto_id=True)
	return render_to_response('reqespecialidadform.html',{'form':form},context_instance=RequestContext(request))

@login_required(login_url=login_url_path)
def nuevo_requerimientosoftware(request, id_oferta):
	if request.method == 'POST':
		form = RequerimientoSoftware_formulario(request.POST)
		if form.is_valid():
			oferta_consulta = Oferta.objects.get(pk=id_oferta)
			estado_oferta = oferta_consulta.enviado
			if not estado_oferta:
				software_form = form.cleaned_data['especialidad']
				estado_form = form.cleaned_data['estado_software']
				software = RequerimientoSoftware(oferta=oferta_consulta, software=software_form, estado_software=estado_form)
				software.save()
				redireccion = '/oferta/' + str(oferta_consulta.id)
				return HttpResponseRedirect(redireccion)
			else:
				return render_to_response('ofertaenviada.html')
	else:
		form = RequerimientoSoftware_formulario(auto_id=True)
	return render_to_response('reqsoftware.html',{'form':form},context_instance=RequestContext(request))

@login_required(login_url=login_url_path)
def nuevo_requerimientoidioma(request, id_oferta):
	if request.method == 'POST':
		form = RequerimientoIdioma_formulario(request.POST)
		if form.is_valid():
			oferta_consulta = Oferta.objects.get(pk=id_oferta)
			estado_oferta = oferta_consulta.enviado
			if not estado_oferta:
				idioma_form = form.cleaned_data['idioma']
				lectura_form = form.cleaned_data['lectura']
				escritura_form = form.cleaned_data['escritura']
				conversacion_form = form.cleaned_data['conversacion']
				idioma = RequerimientoIdioma(idioma=idioma_form, lectura=lectura_form, escritura=escritura_form, conversacion=conversacion_form, oferta=oferta_consulta)
				idioma.save()
				redireccion = '/oferta/' + str(oferta_consulta.id)
				return HttpResponseRedirect(redireccion)
			else:
				return render_to_response('ofertaenviada.html')
	else:
		form = RequerimientoIdioma_formulario(auto_id=True)
	return render_to_response('reqidioma.html',{'form':form},context_instance=RequestContext(request))


@login_required(login_url=login_url_path)
def nueva_funcion(request, id_oferta):
	if request.method == 'POST':
		form = Funcion_formulario(request.POST)
		if form.is_valid():
			oferta_consulta = Oferta.objects.get(pk=id_oferta)
			estado_oferta = oferta_consulta.enviado
			if not estado_oferta:
				descripcion = form.cleaned_data['descripcion_funcion']
				funcion = Funcion(oferta=oferta_consulta, descripcion_funcion=descripcion)
				funcion.save()
				redireccion = '/oferta/' + str(oferta_consulta.id)
				return HttpResponseRedirect(redireccion)
			else:
				return render_to_response('ofertaenviada.html')
	else:
		form = Funcion_formulario(auto_id=True)
	return render_to_response('funcionform.html',{'form':form},context_instance=RequestContext(request)) 

@login_required(login_url=login_url_path)
def nuevo_correoenviaroferta(request, id_oferta):
	if request.method == 'POST':
		form = CorreoEnviarOferta_formulario(request.POST)
		if form.is_valid():
			oferta_consulta = Oferta.objects.get(pk=id_oferta)
			estado_oferta = oferta_consulta.enviado
			if not estado_oferta:
				correo_formulario = form.cleaned_data['correo']
				correo_nuevo = CorreoEnviarOferta(oferta=oferta_consulta, correo=correo_formulario)
				correo_nuevo.save()
				redireccion = '/oferta/'+str(oferta_consulta.id)
				return HttpResponseRedirect(redireccion)
			else:
				return render_to_response('ofertaenviada.html')
	else:
		form = CorreoEnviarOferta_formulario(auto_id=True)
	return render_to_response('correoenviarofertaform.html',{'form':form},context_instance=RequestContext(request)) 

@login_required(login_url=login_url_path)
def ofertas_listado(request):
    datos = Oferta.objects.all().order_by('-pk')
    return render_to_response('ofertalist.html',{'data':datos},context_instance=RequestContext(request))

@login_required(login_url=login_url_path)
def ofertas_detalle(request,id_oferta):
    dato = Oferta.objects.get(pk=id_oferta)
    especialidades = RequerimientoEspecialidad.objects.filter(oferta=dato)
    idiomas = RequerimientoIdioma.objects.filter(oferta=dato)
    funciones = Funcion.objects.filter(oferta=dato)
    correos = CorreoEnviarOferta.objects.filter(oferta=dato)
    software_lista = RequerimientoSoftware.objects.filter(oferta=dato)
    estado_oferta = dato.enviado
    if not estado_oferta:
		if request.method == 'POST':
			if request.POST.has_key('especialidad_elegida'):
				form = RequerimientoEspecialidad_formulario(request.POST)
				if form.is_valid():
					especialidad_form = form.cleaned_data['especialidad_elegida']
					estado_form = form.cleaned_data['estado']
					condicion_form = form.cleaned_data['condicion']
					experiencia_form = form.cleaned_data['anos_experiencia']
					requerimiento = RequerimientoEspecialidad(oferta=dato, especialidad_elegida=especialidad_form, estado=estado_form, condicion=condicion_form, anos_experiencia=experiencia_form)
					requerimiento.save()
			elif request.POST.has_key('descripcion_funcion'):
				form = Funcion_formulario(request.POST)
				if form.is_valid():
					descripcion_form = form.cleaned_data['descripcion_funcion']
					funcion = Funcion(oferta=dato, descripcion_funcion=descripcion_form)
					funcion.save()
			elif request.POST.has_key('estado_software'):
				form = RequerimientoSoftware_formulario(request.POST)
				if form.is_valid():
					software_form = form.cleaned_data['software']
					estado_form = form.cleaned_data['estado_software']
					software = RequerimientoSoftware(oferta=dato, software=software_form, estado_software=estado_form)
					software.save()
			elif request.POST.has_key('idioma'):
				form = RequerimientoIdioma_formulario(request.POST)
				if form.is_valid():
					idioma_form = form.cleaned_data['idioma']
					lectura_form = form.cleaned_data['lectura']
					escritura_form = form.cleaned_data['escritura']
					conversacion_form = form.cleaned_data['conversacion']
					idioma = RequerimientoIdioma(idioma=idioma_form, lectura=lectura_form, escritura=escritura_form, conversacion=conversacion_form, oferta=dato)
					idioma.save()
			elif request.POST.has_key('correo'):
				form = CorreoEnviarOferta_formulario(request.POST)
				if form.is_valid():
					correo_form = form.cleaned_data['correo']
					correo_envio = CorreoEnviarOferta(oferta=dato, correo=correo_form)
					correo_envio.save()
    return render_to_response('ofertadet.html',{'data':dato,'funciones':funciones, 'correos':correos, 'especialidades':especialidades, 'software':software_lista, 'idiomas':idiomas},context_instance=RequestContext(request))

@login_required(login_url=login_url_path)
def publicar_oferta(request, id_oferta):
    dato = Oferta.objects.get(pk=id_oferta)
    if dato.enviado:
		return render_to_response('ofertaenviada.html')
    funciones = Funcion.objects.filter(oferta=dato)
    correos = CorreoEnviarOferta.objects.filter(oferta=dato)
    
    #Datos de publicacion
    mensaje = ''
    titulo_publicar = dato.titulo
    mensaje += dato.sede.empresa.nombre_comercial + "\n"
    mensaje += dato.sede.direccion + "\n"
    mensaje += str(dato.fecha) + "\n"
    mensaje += str(dato.dias) + "\n"
    mensaje += str(dato.vacantes) + "\n"
    mensaje += dato.descripcion + "\n"
    mensaje += dato.area.nombre + "\n"
    mensaje += dato.cargo.nombre + "\n"
    mensaje += dato.tipo_contrato.nombre + "\n"
    if dato.salario:
		mensaje += str(dato.salario) + "\n"
    if dato.beneficio:
		mensaje += dato.beneficio + "\n"
    if dato.requerimiento:
		mensaje += dato.requerimiento + "\n"
    if dato.indicacion:
		mensaje += dato.indicacion + "\n"
    
    mensaje += "Funciones:\n"
    lista_funciones = []
    for funcion in funciones:
        lista_funciones.append(funcion.descripcion_funcion)
        mensaje += funcion.descripcion_funcion + "\n"
    mensaje += "Enviar a:\n"
    lista_correos = []
    for correo in correos:
        lista_correos.append(correo.correo)
        mensaje += correo.correo + "\n"
    
    email = EmailMessage(titulo_publicar,mensaje,to=['sergio@neosergio.net'])
    email.send()
    #~ email = EmailMessage(titulo_publicar,mensaje,to=['jsifuente@continental.edu.pe'])
    #~ email.send()
    #~ email = EmailMessage(titulo_publicar,mensaje,to=['apena@continental.edu.pe'])
    #~ email.send()
    dato.enviado = True
    dato.save()
    redireccion = '/oferta/' + str(id_oferta)
    return HttpResponseRedirect(redireccion)

@login_required(login_url=login_url_path)
def salir(request):
	logout(request)
	return HttpResponseRedirect('/')

@login_required(login_url=login_url_path)
def postulantes(request):
	dato = Postulante.objects.all()
	return render_to_response('postulantes.html',{'dato':dato},context_instance=RequestContext(request))

@login_required(login_url=login_url_path)
def postulante_nuevo(request):
	if request.method == 'POST':
		form = PostulanteFormulario(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/postulantes')
	else:
		form = PostulanteFormulario(auto_id=True)
	return render_to_response('postulanteform.html',{'form':form},context_instance=RequestContext(request)) 

@login_required(login_url=login_url_path)
def postulante_detalle(request, id_postulante):
	dato = Postulante.objects.get(pk=id_postulante)
	return render_to_response('postulantedetalle.html', {'dato':dato}, context_instance=RequestContext(request))

class PostulanteNuevo(CreateView):
	form_class = PostulanteFormulario
	model = Postulante

	def form_valid(self, form):
		form.instance.persona = Persona.objects.get(usuario=self.request.user)
		return super(PostulanteNuevo, self).form_valid(form)

class PostulanteActualiza(UpdateView):
	model = Postulante

class PostulanteBorra(DeleteView):
	model = Postulante
	success_url = reverse_lazy('/')