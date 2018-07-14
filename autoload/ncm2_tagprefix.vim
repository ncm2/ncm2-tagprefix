if get(s:, 'loaded', 0)
    finish
endif
let s:loaded = 1

let g:ncm2_tagprefix#proc = yarp#py3('ncm2_tagprefix')

let g:ncm2_tagprefix#source = extend(
			\ get(g:, 'ncm2_tagprefix#source', {}), {
            \ 'name': 'tagprefix',
            \ 'priority': 6,
            \ 'mark': '#',
            \ 'on_complete': 'ncm2_tagprefix#on_complete',
            \ 'on_warmup': 'ncm2_tagprefix#on_warmup',
            \ }, 'keep')

func! ncm2_tagprefix#init()
    call ncm2#register_source(g:ncm2_tagprefix#source)
endfunc

func! ncm2_tagprefix#on_warmup(ctx)
    call g:ncm2_tagprefix#proc.jobstart()
endfunc

func! ncm2_tagprefix#on_complete(ctx)
    call g:ncm2_tagprefix#proc.try_notify('on_complete', a:ctx, getcwd(), tagfiles())
endfunc

