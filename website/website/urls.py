from django.conf.urls.defaults import patterns, include, url
from joboffers.forms import amarrado, Oferta_formulario, Funcion_formulario, CorreoEnviarOferta_formulario
#from joboffers.views import PostulanteNuevo, PostulanteActualiza, PostulanteBorra
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$','joboffers.views.inicio'),
    url(r'^ingreso/$','joboffers.views.ingresoadmin'),
    url(r'^salir/$','joboffers.views.salir'),
    url(r'^administrar/$','joboffers.views.administrar'),
    url(r'^registro/$','joboffers.views.registro'),
    url(r'^oferta/$','joboffers.views.ofertas_listado'),
    url(r'^oferta/(?P<id_oferta>\d+)/$','joboffers.views.ofertas_detalle'),
    url(r'^oferta/nueva/$','joboffers.views.nueva_oferta'),
    url(r'^oferta/nueva/funcion/(?P<id_oferta>\d+)/$','joboffers.views.nueva_funcion'),
    url(r'^oferta/nueva/correo/(?P<id_oferta>\d+)/$','joboffers.views.nuevo_correoenviaroferta'),
    url(r'^oferta/nueva/especialidad/(?P<id_oferta>\d+)/$','joboffers.views.nuevo_requerimientoespecialidad'),
    url(r'^oferta/nueva/idioma/(?P<id_oferta>\d+)/$','joboffers.views.nuevo_requerimientoidioma'),
    url(r'^oferta/nueva/software/(?P<id_oferta>\d+)/$','joboffers.views.nuevo_requerimientosoftware'),
    url(r'^oferta/publicar/(?P<id_oferta>\d+)/$','joboffers.views.publicar_oferta'),
    #url(r'^amarrado/$', amarrado([Oferta_formulario, Funcion_formulario, CorreoEnviarOferta_formulario])),
    url(r'^root/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$','django.views.static.serve',
		{'document_root':settings.MEDIA_ROOT,}
	),
    url(r'^postulante/$', 'joboffers.views.postulantes'),
    url(r'^postulante/nuevo/$', 'joboffers.views.postulante_nuevo'),
    url(r'^postulante/(?P<id_postulante>\d+)/$', 'joboffers.views.postulante_detalle'),
)
