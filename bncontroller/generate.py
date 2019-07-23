from pathlib import Path
from pandas import DataFrame
from bncontroller.file.utils import get_dir, iso8106
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.stubs.selector.utils import bnselector_generator
from bncontroller.stubs.selector.generation import generate as generate_bnselector

if __name__ == "__main__":

    template = parse_args_to_config()

    N, K, P, I, O = template.bn_n, template.bn_k, template.bn_p, template.bn_n_inputs, template.bn_n_outputs
    # N, K, P, I, O = 5, 2, 0.5, 1, 0

    # bng = bnselector_generator(N, K, P, I, O)
    
    path = get_dir(Path('./tmp/thousand_bns/'), create_if_dir=True)
    date = template.globals['date']

    for l in range(1000):

        # bn = bng.new_selector()

        bn = generate_bnselector(template)

        Path(path / f'{l}_bn_n{N}_k{K}_p{int(P*100)}_{date}.ebnf').write_text(
            bn.to_ebnf()
        )

        df = DataFrame(bn.atm.dtableau)
        # print(df)
        df.to_csv(str(path / f'{l}_atm_{date}.csv'))
    
    exit(1)


