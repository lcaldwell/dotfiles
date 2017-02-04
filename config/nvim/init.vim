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
call dein#add('jistr/vim-nerdtree-tabs')
call dein#add('Xuyuanp/nerdtree-git-plugin')

" Git
call dein#add('airblade/vim-gitgutter')
call dein#add('tpope/vim-fugitive')

" Theme
call dein#add('mhartington/oceanic-next')
call dein#add('vim-airline/vim-airline')
call dein#add('ryanoasis/vim-devicons')

" Navigation
call dein#add('christoomey/vim-tmux-navigator')

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

" }}}------------------------------------------------------------------------------------------------------------------------


" System settings
" ------------------------------------------------------------------------------------------------------------------------{{{
set noshowmode " only show status in airline bar
set termguicolors " allow true colors
let $NVIM_TUI_ENABLE_CURSOR_SHAPE=1 " allow cursor shape to change
set number " enable line numbers
set undofile
set undodir="$HOME/.VIM_UNDO_FILES"
" make esc remove highlighting from search (using /)
nnoremap <esc> :noh<return><esc>
" remap default : to ;
nnoremap ; :
" }}}------------------------------------------------------------------------------------------------------------------------


" Themes
" ------------------------------------------------------------------------------------------------------------------------{{{
syntax on " make sure syntax highlighting is on
colorscheme OceanicNext " Mike Hartingtons OceanicNext colour scheme (added in the packages section)
" }}}------------------------------------------------------------------------------------------------------------------------


" Airline
" ------------------------------------------------------------------------------------------------------------------------{{{
let g:airline_theme='oceanicnext'
let g:airline_powerline_fonts=1 " allow airline to use the powerline fonts
" }}}------------------------------------------------------------------------------------------------------------------------


" NERDTree
" ------------------------------------------------------------------------------------------------------------------------{{{
map <silent> - :NERDTreeTabsToggle<CR>
map <silent> = :NERDTreeFocusToggle<CR>
let NERDTreeMinimalUI=1 " remove helpline at top of NERDTree
" }}}------------------------------------------------------------------------------------------------------------------------


" Navigate between vim buffers and tmux panels
" ------------------------------------------------------------------------------------------------------------------------{{{
let g:tmux_navigator_no_mappings = 1
nnoremap <silent> <C-j> :TmuxNavigateDown<cr>
nnoremap <silent> <C-k> :TmuxNavigateUp<cr>
nnoremap <silent> <C-l> :TmuxNavigateRight<cr>
nnoremap <silent> <C-h> :TmuxNavigateLeft<CR>
nnoremap <silent> <C-;> :TmuxNavigatePrevious<cr>
tmap <C-j> <C-\><C-n>:TmuxNavigateDown<cr>
tmap <C-k> <C-\><C-n>:TmuxNavigateUp<cr>
tmap <C-l> <C-\><C-n>:TmuxNavigateRight<cr>
tmap <C-h> <C-\><C-n>:TmuxNavigateLeft<CR>
tmap <C-;> <C-\><C-n>:TmuxNavigatePrevious<cr>
" }}}------------------------------------------------------------------------------------------------------------------------


" GitGutter
" ------------------------------------------------------------------------------------------------------------------------{{{
let g:gitgutter_sign_column_always = 1
" }}}------------------------------------------------------------------------------------------------------------------------
