from bncontroller.file.utils import generate_file_name, iso8106

app_globals = dict(
    date = iso8106(ms=3),
    score = float('+inf'),
    it = -1,
    top_model_name = f'bn_{iso8106()}'+'{subfix}.json',
    subopt_suffix = '_it{it}',
)