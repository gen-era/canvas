from django import template

register = template.Library()


@register.simple_tag(name="sortedchip", takes_context=True)
def sortedchip(context, chip):
    user = context["user"]

    num_rows = chip.chip_type.rows
    num_cols = chip.chip_type.cols
    chipsamples = chip.chipsample.all()

    if not user.is_staff:
        user_groups = user.groups.all()
        chipsamples = chipsamples.filter(sample__institution__group__in=user_groups)

    chipsample_rows = []
    for row in range(1, num_rows + 1):
        chipsample_cols = []
        for col in range(1, num_cols + 1):
            position = f"R{row:02}C{col:02}"
            chipsample = chipsamples.filter(position=position).first()
            if chipsample:
                if chipsample.sample:
                    chipsample_cols.append(chipsample)
                else:
                    chipsample_cols.append(position)
            else:
                chipsample_cols.append(position)

        chipsample_rows.append(chipsample_cols)
    return chipsample_rows
