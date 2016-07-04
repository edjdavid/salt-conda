create_env:
    conda.create:
        - name: test
        - packages: python=3.5

sci_libs:
    conda.install:
        - name: numpy,scipy,pandas,matplotlib
        - path: /usr/share/anaconda
        - env: test

r_base:
    conda.install:
        - name: r
        - channel: r
        - path: /usr/share/anaconda
        - env: test
