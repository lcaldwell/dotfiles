" Setup dein (package manager) 
" - ':call dein#install()' to install new packages
" ------------------------------------------------------------------------------------------------------------------------{{{

" Required:
set runtimepath+=~/.config/nvim/repos/github.com/Shougo/dein.vim

if (!isdirectory(expand("$HOME/.config/nvim/repos/github.com/Shougo/dein.vim")))
  call system(expand("mkdir -p $HOME/.config/nvim/repos/github.com"))
  call system(expand("git clone https://github.com/Shougo/dein.vim $HOME/.config/nvim/repos/github.com/Shougo/dein.vim"))
endif

" Let dein manage dein
" Required:
call dein#begin(expand('~/.config/nvim'))
call dein#add('Shougo/dein.vim')
call dein#add('Shougo/denite.nvim')

" Deoplete stuff
call dein#add('Shougo/neosnippet.vim')
call dein#add('Shougo/neosnippet-snippets')

" File management
call dein#add('scrooloose/nerdtree')
call dein#add('Xuyuanp/nerdtree-git-plugin')

" Theme
call dein#add('mhartington/oceanic-next')
call dein#add('vim-airline/vim-airline')
call dein#add('ryanoasis/vim-devicons')

" Required:
call dein#end()
call dein#save_state()

" Required:
filetype plugin indent on
syntax enable

" If you want to install not installed plugins on startup.
"if dein#check_install()
"  call dein#install()
"endif

" }}}-----------------------------------------------------------------------------------------------------------------------


" System settings
" ------------------------------------------------------------------------------------------------------------------------{{{
set noshowmode " only show status in airline bar
set termguicolors " allow true colors
let $NVIM_TUI_ENABLE_CURSOR_SHAPE=1 " allow cursor shape to change
set number " enable line numbers
" }}}------------------------------------------------------------------------------------------------------------------------


" Themes
" ------------------------------------------------------------------------------------------------------------------------{{{
syntax on " make sure syntax highlighting is on
colorscheme OceanicNext " Mike Hartingtons OceanicNext colour scheme (added in the packages section)

let g:airline_theme='oceanicnext'
" }}}------------------------------------------------------------------------------------------------------------------------


" NERDTree 
" ------------------------------------------------------------------------------------------------------------------------{{{
let g:NERDTreeIndicatorMapCustom = {
    \ "Modified"  : "✹",
    \ "Staged"    : "✚",
    \ "Untracked" : "✭",
    \ "Renamed"   : "➜",
    \ "Unmerged"  : "═",
    \ "Deleted"   : "✖",
    \ "Dirty"     : "✗",
    \ "Clean"     : "✔︎",
    \ "Unknown"   : "?"
    \ }
" }}}------------------------------------------------------------------------------------------------------------------------
