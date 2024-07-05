from django_components import component

from canvas.models import Sample


@component.register("tbody_sample_search")
class TBodysampleSearchComponent(component.Component):
    template = """
        {% for sample in samples %}
            <tr class="tr"> 
                <td class="td">{{ sample.protocol_id }}</td>
                <td class="td">{{ sample.sample_type }}</td>
                <td class="td">{{ sample.arrival_date }}</td>
                <td class="td">{{ sample.institution.name }}</td>
            </tr>
        {% endfor %}
    """

    def post(self, request, **kwargs):
        search = request.POST.get("search")
        if not search:
            return self.render_to_response({})
        samples = Sample.objects.filter(
            protocol_id__icontains=search
        ) | Sample.objects.filter(sample_type__name__icontains=search)
        context = {"samples": samples.order_by("id")[:10]}
        return self.render_to_response(context)
