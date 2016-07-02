class Log:
    @staticmethod
    def write(indent, text):
        indent = " " * 2 * indent
        print("MK8MUUNT: " + indent + text)
