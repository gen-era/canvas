from django_components import component

from canvas.models import Institution


@component.register("tbody_institution_search")
class TBodyinstitutionSearchComponent(component.Component):
    template = """
        {% for institution in institutions %}
            <tr class="tr"> 
                <td class="td">{{ institution.name }}</td>
            </tr>
        {% endfor %}
    """

    def post(self, request, **kwargs):
        search = request.POST.get("search")
        if not search:
            return self.render_to_response({})
        institutions = Institution.objects.filter(name__icontains=search)
        context = {"institutions": institutions.order_by("id")[:10]}
        return self.render_to_response(context)
