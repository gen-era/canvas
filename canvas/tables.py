import django_tables2 as tables

def create_table_class(model):
    Meta = type('Meta', 
                (object,), 
                {'model': model, 
                 'template_name': "canvas/bootstrap_htmx.html"})
    DynamicTable = type('DynamicTable', (tables.Table,), {'Meta': Meta})

    return DynamicTable
