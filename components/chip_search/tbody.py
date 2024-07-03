from django_components import component

from canvas.models import Chip


@component.register("tbody_chip_search")
class TBodyChipSearchComponent(component.Component):
    template = """
        {% for chip in chips %}
            <tr class="tr"> 
                <td class="td">{{ chip.chip_id }}</td>
                <td class="td">{{ chip.chip_type }}</td>
                <td class="td">{{ chip.scan_date }}</td>
            </tr>
        {% endfor %}
    """

    def post(self, request, **kwargs):
        search = request.POST.get("search")
        if not search:
            return self.render_to_response({})
        chips = Chip.objects.filter(chip_id__icontains=search) | Chip.objects.filter(
            chip_type__name__icontains=search
        )
        print("hi")
        print(Chip.objects.all())
        print(chips)
        context = {"chips": chips.order_by("id")[:10]}
        return self.render_to_response(context)
