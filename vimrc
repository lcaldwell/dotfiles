set nocompatible
filetype off
set rtp+=~/.vim/bundle/Vundle.vim/
call vundle#begin()

Plugin 'VundleVim/Vundle.vim'

"--- Appearance ---
Plugin 'wombat256.vim'
Plugin 'itchyny/lightline.vim'

"--- Files ---
Plugin 'scrooloose/nerdtree'
Plugin 'jistr/vim-nerdtree-tabs'

"--- Error checking ---
Plugin 'vim-syntastic/syntastic'

Plugin 'xolox/vim-misc'
Plugin 'xolox/vim-easytags'
Plugin 'majutsushi/tagbar'
Plugin 'ctrlpvim/ctrlp.vim'
Plugin 'airblade/vim-gitgutter'

call vundle#end() 
filetype plugin indent on

"------------------------


"--- General Settings ---
set number "Show line numbers
set ruler "Show cursor position (line and column)
set showcmd "Show partial command in last line
set incsearch "Match search patterns as you type them
set hlsearch "Highlight previous search matches
set laststatus=2
hi clear SignColumn

syntax on "Syntax highlighting

"--- Appearance ---
colorscheme wombat256mod
hi Normal ctermbg=none 
hi NonText ctermbg=none ctermfg=241
let g:lightline = {
      \ 'colorscheme': 'wombat',
      \ }

"--- Tabs ---
" Open/close NERDTree Tabs with \t
nmap <silent> <leader>t :NERDTreeTabsToggle<CR>
" To have NERDTree always open on startup
"let g:nerdtree_tabs_open_on_console_startup = 1

" ----- scrooloose/syntastic settings -----
let g:syntastic_error_symbol = '✘'
let g:syntastic_warning_symbol = "▲"
let g:syntastic_always_populate_loc_list = 1
let g:syntastic_auto_loc_list = 1
let g:syntastic_check_on_open = 1
let g:syntastic_check_on_wq = 0
augroup mySyntastic
  au!
  au FileType tex let b:syntastic_mode = "passive"
augroup END

" ----- xolox/vim-easytags settings -----
" Where to look for tags files
set tags=./tags;,~/.vimtags
" Sensible defaults
let g:easytags_events = ['BufReadPost', 'BufWritePost']
let g:easytags_async = 1
let g:easytags_dynamic_files = 2
let g:easytags_resolve_links = 1
let g:easytags_suppress_ctags_warning = 1

" ----- majutsushi/tagbar settings -----
" Open/close tagbar with \b
nmap <silent> <leader>b :TagbarToggle<CR>
" Uncomment to open tagbar automatically whenever possible
"autocmd BufEnter * nested :call tagbar#autoopen(0)

