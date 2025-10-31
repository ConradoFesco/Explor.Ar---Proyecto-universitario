"""
Blueprint para rutas principales de la aplicación (versión final).
Templates completamente limpios sin JavaScript, usando macros Jinja2.
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from src.core.models.user import User
from src.web.forms import (
    CreateUserForm, UpdateUserForm, UserListForm,
    CreateSiteForm, UpdateSiteForm, SiteListForm,
    CreateTagForm, UpdateTagForm, TagListForm
)
from src.core.services.usuario_service import user_service
from src.core.services.HistoricSite_Service import historic_site_service
from src.core.services.tag_service import tag_service

main_final = Blueprint('main_final', __name__)


@main_final.route("/")
def index():
    """Página de inicio/login"""
    return render_template("auth/login.html")


@main_final.route("/home")
def home():
    """Página principal después del login"""
    if "user_id" not in session:
        return redirect(url_for("main_final.index"))
    user = User.query.get(session["user_id"])
    return render_template("shared/home.html", user=user)


@main_final.route("/logout")
def logout():
    """Cierra la sesión del usuario"""
    session.pop("user_id", None)
    return redirect(url_for("main_final.index"))


# ===== RUTAS DE USUARIOS =====

@main_final.route("/users")
def list_users():
    """Lista de usuarios"""
    if "user_id" not in session:
        return redirect(url_for("main_final.index"))
    
    # Obtener parámetros de filtrado
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    
    filters = {
        "email": request.args.get('search'),
        "activo": request.args.get('activo'),
        "rol": request.args.get('rol')
    }
    filters = {k: v for k, v in filters.items() if v}
    
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    try:
        # Obtener usuarios del servicio
        result = user_service.list_users(
            filters=filters, 
            page=page, 
            per_page=per_page, 
            sort_by=sort_by, 
            sort_order=sort_order
        )
        
        users = result.get("users", [])
        pagination = {
            "page": result.get("page", page),
            "per_page": result.get("per_page", per_page),
            "total": result.get("total", 0),
            "pages": result.get("pages", 1),
            "has_prev": result.get("has_prev", False),
            "has_next": result.get("has_next", False),
            "prev_num": result.get("prev_num"),
            "next_num": result.get("next_num"),
        }
        
        return render_template('pages/users/index.html.jinja', 
                             users=users, 
                             pagination=pagination)
    except Exception as e:
        flash(f'Error al cargar usuarios: {str(e)}', 'error')
        return render_template('pages/users/index.html.jinja', 
                             users=[], 
                             pagination={})


@main_final.route('/users/create', methods=['GET', 'POST'])
def create_user():
    """Formulario de creación de usuario"""
    if "user_id" not in session:
        return redirect(url_for("main_final.index"))
    
    # Obtener roles disponibles
    try:
        available_roles = user_service.get_available_roles()
    except:
        available_roles = []
    
    form = CreateUserForm(available_roles=available_roles)
    
    if form.validate_on_submit():
        try:
            # Preparar datos para el servicio
            user_data = session.get('user_id')
            data_new_user = {
                'mail': form.mail.data,
                'name': form.name.data,
                'last_name': form.last_name.data,
                'password': form.password.data,
                'active': form.active.data,
                'blocked': form.blocked.data,
                'roles': form.roles.data
            }
            
            # Crear usuario
            result = user_service.create_user(user_data, data_new_user)
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('main_final.list_users'))
            
        except Exception as e:
            flash(f'Error al crear usuario: {str(e)}', 'error')
    
    return render_template('pages/users/create.html.jinja', form=form)


@main_final.route("/users/<int:user_id>/edit", methods=['GET', 'POST'])
def edit_user(user_id):
    """Formulario de edición de usuario"""
    if "user_id" not in session:
        return redirect(url_for("main_final.index"))
    
    try:
        # Obtener datos del usuario
        user_data = user_service.get_user(user_id)
        available_roles = user_service.get_available_roles()
        
        form = UpdateUserForm(available_roles=available_roles)
        
        if request.method == 'GET':
            # Cargar datos existentes
            form.user_id.data = user_data['id']
            form.mail.data = user_data['mail']
            form.name.data = user_data['name']
            form.last_name.data = user_data['last_name']
            form.active.data = user_data['active']
            form.blocked.data = user_data['blocked']
            # Cargar roles existentes
            if 'roles' in user_data:
                form.roles.data = [role['id'] for role in user_data['roles']]
        
        if form.validate_on_submit():
            try:
                # Preparar datos para actualización
                admin_user_id = session.get('user_id')
                changed_fields = {
                    'mail': form.mail.data,
                    'name': form.name.data,
                    'last_name': form.last_name.data,
                    'active': form.active.data,
                    'blocked': form.blocked.data,
                    'roles': form.roles.data
                }
                
                # Actualizar usuario
                result = user_service.update_user(user_id, changed_fields, admin_user_id)
                flash('Usuario actualizado exitosamente', 'success')
                return redirect(url_for('main_final.list_users'))
                
            except Exception as e:
                flash(f'Error al actualizar usuario: {str(e)}', 'error')
        
        return render_template('pages/users/edit.html.jinja', form=form, user_data=user_data)
        
    except Exception as e:
        flash(f'Error al cargar usuario: {str(e)}', 'error')
        return redirect(url_for('main_final.list_users'))


# ===== RUTAS DE SITIOS HISTÓRICOS =====

@main_final.route("/sites")
def lista_sitios():
    """Lista de sitios históricos"""
    if "user_id" not in session:
        return redirect(url_for("main_final.index"))
    
    # Obtener opciones para filtros
    try:
        filter_options = historic_site_service.get_filter_options()
        cities = filter_options.get('cities', [])
    except:
        cities = []
    
    # Obtener parámetros de filtrado
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    
    # Aplicar filtros
    search_text = request.args.get('search')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    city_id = request.args.get('city_id', type=int)
    visible_param = request.args.get('visible')
    visible = None
    if visible_param:
        visible = visible_param.lower() == 'true'
    
    try:
        # Obtener sitios del servicio
        result = historic_site_service.get_all_historic_sites(
            include_deleted=False,
            page=page,
            per_page=per_page,
            search_text=search_text,
            sort_by=sort_by,
            sort_order=sort_order,
            city_id=city_id,
            visible=visible
        )
        
        sites = result.get('sites', [])
        pagination = result.get('pagination', {})
        
        return render_template('pages/sites/index.html.jinja', 
                             sites=sites, 
                             pagination=pagination,
                             cities=cities)
    except Exception as e:
        flash(f'Error al cargar sitios: {str(e)}', 'error')
        return render_template('pages/sites/index.html.jinja', 
                             sites=[], 
                             pagination={},
                             cities=cities)


@main_final.route("/sites/create", methods=['GET', 'POST'])
def alta_sitios():
    """Formulario de alta de sitios"""
    if "user_id" not in session:
        return redirect(url_for("main_final.index"))
    
    # Obtener opciones para el formulario
    try:
        filter_options = historic_site_service.get_filter_options()
        form = CreateSiteForm(
            categories=filter_options.get('categories', []),
            states=filter_options.get('states', []),
            tags=filter_options.get('tags', [])
        )
    except:
        form = CreateSiteForm()
    
    if form.validate_on_submit():
        try:
            # Preparar datos para el servicio
            data_user = session.get('user_id')
            data_site = {
                'name': form.name.data,
                'brief_description': form.brief_description.data,
                'complete_description': form.complete_description.data,
                'name_city': form.name_city.data,
                'name_province': form.name_province.data,
                'latitude': form.latitude.data,
                'longitude': form.longitude.data,
                'year_inauguration': form.year_inauguration.data,
                'id_category': form.id_category.data,
                'id_estado': form.id_estado.data,
                'visible': form.visible.data,
                'tags': form.tags.data
            }
            
            # Crear sitio
            result = historic_site_service.create_historic_site(data_site, data_user)
            flash('Sitio histórico creado exitosamente', 'success')
            return redirect(url_for('main_final.lista_sitios'))
            
        except Exception as e:
            flash(f'Error al crear sitio: {str(e)}', 'error')
    
    return render_template('pages/sites/create.html.jinja', form=form)


# ===== RUTAS DE TAGS =====

@main_final.route("/tags")
def lista_tags():
    """Lista de tags"""
    if "user_id" not in session:
        return redirect(url_for("main_final.index"))
    
    # Obtener parámetros de filtrado
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    
    search_text = request.args.get('search')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    try:
        # Obtener tags del servicio
        result = tag_service.get_all_tags(
            page=page,
            per_page=per_page,
            search_text=search_text,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        tags = result.get('tags', [])
        pagination = result.get('pagination', {})
        
        return render_template('pages/tags/index.html.jinja', 
                             tags=tags, 
                             pagination=pagination)
    except Exception as e:
        flash(f'Error al cargar tags: {str(e)}', 'error')
        return render_template('pages/tags/index.html.jinja', 
                             tags=[], 
                             pagination={})


