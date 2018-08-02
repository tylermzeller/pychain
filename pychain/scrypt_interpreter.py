import pychain.scrypt_defs as scrypt_defs
import pychain.scrypt_defs.ScryptError as ScryptError

def return_success():
    return True, ScryptError.SCRIPT_ERR_OK

def return_error(error):
    return False, error

def evaluate(self, stack, script):
    # TODO: implement script object
    pc = script.begin()
    pend = script.end()
    try:
        while pc < pend:
            pass # TODO implement evaluation logic: see https://github.com/bitcoin/bitcoin/blob/master/src/script/interpreter.cpp#L306
    except:
        return return_error(ScryptError.SCRIPT_ERR_UNKNOWN_ERROR)

    return return_success()
