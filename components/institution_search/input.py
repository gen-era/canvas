from django_components import component


@component.register("input_institution_search")
class InputinstitutionSearchComponent(component.Component):
    template = """
        <div class="mb-4 w-[256px]">
            <input class="input form-control" type="search" 
                name="search" placeholder="Search for a institution"
                hx-post="{% url 'tbody_institution_search' %}"
                hx-trigger="input changed delay:500ms, search" 
                hx-target="#institution-results">
        </div>
        <table class="table">
            <thead class="thead">
                <tr>
                    <th class="th">institution Id</th>
                    <th class="th">institution Type</th>
                    <th class="th">Scan Date</th>
                </tr>
            </thead>
            <tbody id="institution-results">
            </tbody>
        </table>
    """
