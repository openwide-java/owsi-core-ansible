# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
DOCDIR				= docs
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(DOCDIR)/$(SOURCEDIR)" "$(DOCDIR)/$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile livehtml

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(DOCDIR)/$(SOURCEDIR)" "$(DOCDIR)/$(BUILDDIR)" $(SPHINXOPTS) $(O)
