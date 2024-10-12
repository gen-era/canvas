from django import template

register = template.Library()

@register.filter(name="sortedchip")
def sortedchip(chip):
    num_rows = chip.chip_type.rows
    num_cols = chip.chip_type.cols
    chipsamples = chip.chipsample.all()

    chipsample_cols = []
    for col in range(1, num_cols + 1):
        chipsample_rows = []
        for row in range(1, num_rows +1):
            position = f"R{row:02}C{col:02}"
            chipsample = chipsamples.filter(position=position).first()
            if chipsample:
                chipsample_rows.append(chipsample)
            else:
                chipsample_rows.append(position)

        chipsample_cols.append(chipsample_rows)
    return chipsample_cols
