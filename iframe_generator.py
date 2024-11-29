from pathlib import Path

# Path to the directory containing the data
input_dir = Path('./data/scopus')

count_dir = Path('./detailed_counts/')
plotly_output = count_dir / 'charts'
full_output = count_dir / 'full_output'

full_output.mkdir(parents=True, exist_ok=True)

with open(full_output / 'index.html', 'w') as f:
    f.write("""
    <html>
    <head>
        <title>Full output</title>
        <base href="..">
        <style>
            body {
                margin: 0;
                padding: 0;
            }
            /* display div as sticky bar on top */
            div {
                display: flex;
                flex-direction: column;
                height: 100%;
                overflow-y: scroll;
                    width: 120pt;
            }
            /* style the buttons */
            button {
                font-size: 1.5em;
                width: 100%;
                text-align: center;
            }
            iframe {
                border: none;
                flex-grow: 1;
            }
            body {
                display: flex;
                flex-direction: row;
            }
            
            button.active {
                background-color: grey;
            }
        </style>
    </head>
    <body>
        <div>
    """)

for csv_file in input_dir.glob('*.csv'):
    base = csv_file.name
    gauge = plotly_output / f'{base}.html'
    pie1 = plotly_output / f'{base}_DistribClean.html'
    pie2 = plotly_output / f'{base}_DistribUnclean.html'
    jaccard = plotly_output/f'../../results/jaccard_clean_{base}_pie.html'
    #productivity_distrib = path-to-productivity-distrib

    with open(full_output / f'{base}_full.html', 'w') as f:
        f.write(f"""
        <html>
        <head>
            <title>{base}</title>
            <base href="../..">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                }}
                iframe {{
                    border: none;
                }}
            </style>
        </head>
        <body>
            <div style="width: 100%">
                <div>
                    <iframe src="{gauge}" width="100%" height="100%"></iframe>
                </div>
                <div style="display: flex; flex-direction: row; height: 100vh">
                    <iframe src="{pie1}" width="50%" height="100%"></iframe>
                    <iframe src="{pie2}" width="50%" height="100%"></iframe>
                </div>"""
                # <div>
                #     <iframe src="{jaccard}" width="100%" height="100%"></iframe>
                # <div>
                # <div>
                #     <iframe src="{productivity_distrib}" width="100%" height="100%"></iframe>
                # <div>
            """</div>
        </body>
        </html>
        """)
        with open(full_output / 'index.html', 'a') as index:
            index.write(f'<a href="full_output/{base}_full.html" target="content"><button>{csv_file.stem}</button></a>\n')

with open(full_output / 'index.html', 'a') as f:
    f.write("""
        </div>
        <iframe name="content" width="100%"></iframe>
        <script>
            const buttons = document.querySelectorAll('button');
            buttons.forEach((button, i) => {
                button.addEventListener('click', () => {
                    buttons.forEach((b) => b.classList.remove('active'));
                    button.classList.add('active');
                });
            });
            
            buttons[0].click();
        </script>
    </body>
    </html>
    """)