## Docs tutorial

---

Before starting, if you haven't installed `sphinx` and its required dependencies, make sure to run the following commands:

```Bash
pip3 install sphinx
```

```Bash
pip3 install sphinx-apidoc
```

```Bash
pip3 install sphinx-rtd-theme
```

---

To generate docs, run the following command inside the working directory:

```Bash
sphinx-apidoc -o docs .
```

followed by this command inside the `docs` directory:

```Bash
make html
```

---

The `index.html` file can be found at [/elections/docs/_build/html/index.html](_build/html/index.html).