from django_components import component


@component.register("input_chip_search")
class InputChipSearchComponent(component.Component):
    template = """
        <div class="mb-4 w-[256px]">
            <input class="input form-control" type="search" 
                name="search" placeholder="Search for a chip"
                hx-post="{% url 'tbody_chip_search' %}"
                hx-trigger="input changed delay:500ms, search" 
                hx-target="#search-results">
        </div>
        <table class="table">
            <thead class="thead">
                <tr>
                    <th class="th">Chip Id</th>
                    <th class="th">Chip Type</th>
                    <th class="th">Scan Date</th>
                </tr>
            </thead>
            <tbody id="search-results">
            </tbody>
        </table>
    """
