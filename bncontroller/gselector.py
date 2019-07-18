import time
 
from bncontroller.file.utils import get_dir
from bncontroller.jsonlib.utils import write_json
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.stubs.selector.training import search as search_bnselector

########################################################################### 
         
if __name__ == "__main__":
    
    template = parse_args_to_config()

    t = time.perf_counter()
        
    bn, (it, score, *_) = search_bnselector(template)
    
    print(time.perf_counter() - t, end='\n\n')
        
    print(it)
    print(bn.attractors_input_map)
    print(bn.get_atm(from_cache=True).dtableau)
    print(bn.get_atm(from_cache=True).dattractors)

    if not bn.attractors_input_map or None in bn.attractors_input_map:
        print('Failure.')
    else:
        write_json(bn, get_dir(template.bn_selector_path) / 'bn_selector_{date}.json'.format(
            date=template.globals['date']
        ), indent=True)

    exit(1)


