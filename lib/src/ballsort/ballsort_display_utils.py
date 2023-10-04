from IPython.display import display, Javascript

def open_bs_window(url="https://aheed.github.io/ballsort/"):
    dist_obj = Javascript(f"""
        const bsWindow = window.open('{url}', 'bswindow', 'height=700, width=600');
        window.bswin = bsWindow.window;
        """);
    display(dist_obj)
