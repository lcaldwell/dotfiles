if g:dein#_cache_version != 100 | throw 'Cache loading error' | endif
let [plugins, ftplugin] = dein#load_cache_raw(['/Users/lukecaldwell/.config/nvim/init.vim'])
if empty(plugins) | throw 'Cache loading error' | endif
let g:dein#_plugins = plugins
let g:dein#_ftplugin = ftplugin
let g:dein#_base_path = '/Users/lukecaldwell/.dotfiles/config/nvim'
let g:dein#_runtime_path = '/Users/lukecaldwell/.dotfiles/config/nvim/.cache/init.vim/.dein'
let g:dein#_cache_path = '/Users/lukecaldwell/.dotfiles/config/nvim/.cache/init.vim'
let &runtimepath = '/Users/lukecaldwell/.config/nvim,/etc/xdg/nvim,/Users/lukecaldwell/.local/share/nvim/site,/usr/local/share/nvim/site,/Users/lukecaldwell/.dotfiles/config/nvim/.cache/init.vim/.dein,/usr/share/nvim/site,/usr/local/Cellar/neovim/0.1.7/share/nvim/runtime,/usr/share/nvim/site/after,/usr/local/share/nvim/site/after,/Users/lukecaldwell/.local/share/nvim/site/after,/etc/xdg/nvim/after,/Users/lukecaldwell/.config/nvim/after,/Users/lukecaldwell/.dotfiles/config/nvim/repos/github.com/Shougo/dein.vim,/Users/lukecaldwell/.dotfiles/config/nvim/.cache/init.vim/.dein/after'
filetype off
