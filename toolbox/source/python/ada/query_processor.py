import query_calc
import query_show
import query_time

def process_query(args):
    if 'calc' in args:
        print(query_calc.eval_expr(*args[args.index('calc')+1:]))
    elif 'show' in args:
        query_show.process_show(*args[args.index('show')+1:])
    else:
        query_time.process_time_query(*args)
