from django_components import component


@component.register("input_sample_search")
class InputsampleSearchComponent(component.Component):
    template = """
        <div class="mb-4 w-[256px]">
            <input class="input form-control" type="search" 
                name="search" placeholder="Search for a sample"
                hx-post="{% url 'tbody_sample_search' %}"
                hx-trigger="input changed delay:500ms, search" 
                hx-target="#sample-results">
        </div>
        <table class="table">
            <thead class="thead">
                <tr>
                    <th class="th">sample Id</th>
                    <th class="th">sample Type</th>
                    <th class="th">Scan Date</th>
                </tr>
            </thead>
            <tbody id="sample-results">
            </tbody>
        </table>
    """
