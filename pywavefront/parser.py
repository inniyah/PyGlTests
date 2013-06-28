import warnings

class Parser(object):
    """This defines a generalized parse dispatcher; all parse functions
    reside in subclasses."""

    def read_file(self, file_name):
        for line in open(file_name, "r"):
            self.parse(line)

    def parse(self, line):
        """Determine what type of line we are and dispatch
        appropriately."""
        if line.startswith('#'): return

        values = line.split()
        if len(values) < 2: return

        line_type = values[0]
        args = values[1:]

        try:
            parse_function = getattr(self, 'parse_%s'%line_type)
        except AttributeError:
            warnings.warn(
                    '%s ignored unhandled line: %s'%(type(self), line))
            return
        parse_function(args)