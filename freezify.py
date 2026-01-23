from direct.dist import FreezeTool
import sys, os

if sys.version_info[:2] != (3, 12):
    sys.exit("Run this with Python 3.12, or edit this script")

THIS_DIR = r'/home/linuxvm/freezer'
BUNDLE_DIR = THIS_DIR + r"/emscripten-panda3d-bundle"

# Python built for target
PY_INCLUDE_DIR = BUNDLE_DIR + r"/python/include/python3.12"
PY_LIB_DIR = BUNDLE_DIR + r"/python/lib"
PY_LIBS = r"libpython3.12.a", r"libmpdec.a", #"libexpat.a", "libHacl_Hash_SHA2.a"

# Python extension modules
PY_MODULE_DIR = PY_LIB_DIR + r"/python/lib/python3.12/lib-dynload"
PY_STDLIB_DIR = PY_LIB_DIR + r"/python/lib/python3.12"
PY_MODULES = []

# Panda modules / libraries
PANDA_BUILT_DIR = BUNDLE_DIR + "/panda3d-opt"
#PANDA_BUILT_DIR = BUNDLE_DIR + "/panda3d"
PANDA_MODULES = ["core", "direct", "ai", "physics"]
PANDA_LIBS = ["libpanda", "libpandaexpress", "libp3dtool", "libp3dtoolconfig", "libp3webgldisplay", "libp3direct", "libp3openal_audio", "libpandaai", "libpandaphysics"]
PANDA_STATIC = True # built with --static

# Increase this when emscripten complains about running out of memory
INITIAL_HEAP = 3120 * 65536
STACK_SIZE = 1048576
ALLOW_MEMORY_GROWTH = True

# Increase this to get useful debugging info when crashes occur
ASSERTIONS = 0
OPTIMIZE_LEVEL = 3 # 0-3
DEBUG_LEVEL = 0 # up to 4
PY_VERBOSE = False

# Files to preload into the virtual filesystem
# You don't need to preload these files anymore, Panda3D will happily read them
# from the web server instead, but preloading is considerably more efficient.
PRELOAD_FILES = [
    'assets/audio/click.ogg',
'assets/audio/tutorial.mp4',
'assets/fonts/Hacked_CRT.ttf',
'assets/fonts/Micro5-Regular.ttf',
'assets/fonts/propaganda.ttf',
'assets/images/aboutIcon.png',
'assets/images/audioIcon.png',
'assets/images/batteryUpgradeIcon.png',
'assets/images/exitIcon.png',
'assets/images/hullUpgradeIcon.png',
'assets/images/keyboardIcon.png',
'assets/images/mainMenuBackground.png',
'assets/images/motorUpgradeIcon.png',
'assets/images/mouseIcon.png',
'assets/images/optionIcon.png',
'assets/images/optionMenuBg.png',
'assets/images/particletexture.png',
'assets/images/pauseIcon.png',
'assets/images/playIcon.png',
'assets/images/skybox.jpg',
'assets/images/tutorialIcon.png',
'assets/images/world_bg.png',
'assets/models/aidotupdater.bam',
'assets/models/animation.bam',
'assets/models/aquaticRover.bam',
'assets/models/arrow.bam',
'assets/models/bigFish-hit.bam',
'assets/models/bigFish.bam',
'assets/models/biggestFish-hit.bam',
'assets/models/biggestFish.bam',
'assets/models/europa.bam',
'assets/models/hitanimation.bam',
'assets/models/leftJet.bam',
'assets/models/Material.001\ Base\ Color.png',
'assets/models/mountainPeak.bam',
'assets/models/researchModel.bam',
'assets/models/rightJet.bam',
'assets/models/Rover.bam',
'assets/models/roverSubBody.bam',
'assets/models/skybox.bam',
'assets/models/smallFish-hit.bam',
'assets/models/smallFish.bam',
'assets/models/sun.bam',
'assets/models/worldTriangles.bam',
'assets/models/worldVisible.bam',
'assets/models/ZombieMan.bam',
'assets/particles/researchParticles.ptf',
'assets/shaders/ak47Shader.sha',
'assets/shaders/cg2glsl.py',
'assets/shaders/Shader.frag',
'assets/shaders/Shader.vert',
'assets/shaders/shadow_depth.frag',
'assets/shaders/shadow_depth.vert',
'assets/shaders/WorldShader.sha',
'assets/shaders/world_bg.frag.glsl',
'assets/shaders/world_bg.vert.glsl',
]

# Models to convert to .bam
CONVERT_MODELS = [
]
CONVERT_MODELS_EMBED_TEXTURES = True

for model in CONVERT_MODELS:
    PRELOAD_FILES.append(model + ".bam")


class EmscriptenEnvironment:
    platform = 'emscripten'

    pythonInc = PY_INCLUDE_DIR
    pythonLib = ""
    for lib in PY_LIBS:
        lib_path = PY_LIB_DIR + "/" + lib
        if os.path.isfile(lib_path):
            pythonLib += lib_path + " "

    modStr = " ".join((os.path.join(PY_MODULE_DIR, a + ".cpython-312.o") for a in PY_MODULES))

    pandaFlags = ""
    for mod in PANDA_MODULES:
        if PANDA_STATIC:
            pandaFlags += f" {PANDA_BUILT_DIR}/lib/libpy.panda3d.{mod}.cpython-312-wasm32-emscripten.a"
        else:
            pandaFlags += f" {PANDA_BUILT_DIR}/panda3d/{mod}.cpython-312-wasm32-emscripten.o"

    for lib in PANDA_LIBS:
        pandaFlags += f" {PANDA_BUILT_DIR}/lib/{lib}.a"

    pandaFlags += f" -I{PANDA_BUILT_DIR}/include"
    pandaFlags += " -s USE_ZLIB=1 -s USE_VORBIS=1 -s USE_LIBPNG=1 -s USE_FREETYPE=1 -s USE_HARFBUZZ=1 -s ERROR_ON_UNDEFINED_SYMBOLS=0 -s DISABLE_EXCEPTION_THROWING=0 "

    for file in PRELOAD_FILES:
        pandaFlags += " --preload-file " + file

    if ALLOW_MEMORY_GROWTH:
        pandaFlags += " -s ALLOW_MEMORY_GROWTH=1"

    debugFlags = f"-O{OPTIMIZE_LEVEL}"
    if DEBUG_LEVEL:
        debugFlags = f"{debugFlags} -g{DEBUG_LEVEL}"

    compileObj = f"emcc {debugFlags} -fno-exceptions -fno-rtti -c -o %(basename)s.o %(filename)s -I{pythonInc}"
    linkExe = f"emcc {debugFlags} -s INITIAL_HEAP={INITIAL_HEAP} -s STACK_SIZE={STACK_SIZE} -s ASSERTIONS={ASSERTIONS} -s MAX_WEBGL_VERSION=2 -s NO_EXIT_RUNTIME=1 -fno-exceptions -fno-rtti -o %(basename)s.js %(basename)s.o {modStr} {pythonLib} {pandaFlags}"
    linkDll = f"emcc -O2 -shared -o %(basename)s.o %(basename)s.o {pythonLib}"

    compileObj += f" -DPY_VERBOSE={int(PY_VERBOSE)}"

    # Paths to Python stuff.
    Python = None
    PythonIPath = pythonInc
    PythonVersion = "3.12"

    suffix64 = ''
    dllext = ''
    arch = ''

    def compileExe(self, filename, basename, extraLink=[]):
        compile = self.compileObj % {
            'python' : self.Python,
            'filename' : filename,
            'basename' : basename,
            }
        print(compile, file=sys.stderr)
        if os.system(compile) != 0:
            raise Exception('failed to compile %s.' % basename)

        link = self.linkExe % {
            'python' : self.Python,
            'filename' : filename,
            'basename' : basename,
            }
        link += ' ' + ' '.join(extraLink)
        print(link, file=sys.stderr)
        if os.system(link) != 0:
            raise Exception('failed to link %s.' % basename)

    def compileDll(self, filename, basename, extraLink=[]):
        compile = self.compileObj % {
            'python' : self.Python,
            'filename' : filename,
            'basename' : basename,
            }
        print(compile, file=sys.stderr)
        if os.system(compile) != 0:
            raise Exception('failed to compile %s.' % basename)

        link = self.linkDll % {
            'python' : self.Python,
            'filename' : filename,
            'basename' : basename,
            'dllext' : self.dllext,
            }
        link += ' ' + ' '.join(extraLink)
        print(link, file=sys.stderr)
        if os.system(link) != 0:
            raise Exception('failed to link %s.' % basename)


freezer = FreezeTool.Freezer()
freezer.frozenMainCode = """
#include "Python.h"
#include <emscripten.h>
#include <emscripten/html5.h>

extern PyObject *PyInit_core();
extern PyObject *PyInit_direct();
extern PyObject *PyInit_ai();
extern PyObject *PyInit_physics();

extern void init_libOpenALAudio();
extern void init_libpnmimagetypes();
extern void init_libwebgldisplay();

extern void task_manager_poll();

void do_poll() {
    task_manager_poll();
    if (PyErr_Occurred()) {
        PyErr_Print();
        printf("Exception occurred, see JavaScript console for details\\n");
        emscripten_cancel_main_loop();
        emscripten_exit_pointerlock();
    }
}

int
Py_FrozenMain(int argc, char **argv)
{
    PyConfig config;
    PyConfig_InitIsolatedConfig(&config);
    config.pathconfig_warnings = 0;
    config.use_environment = 0;
    config.write_bytecode = 0;
    config.site_import = 0;
    config.user_site_directory = 0;
    config.buffered_stdio = 0;
    config.verbose = PY_VERBOSE;

    PyStatus status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
        return 1;
    }
    fprintf(stderr, "Python %s\\n", Py_GetVersion());

    PyConfig_Clear(&config);

    PyObject *panda3d_module = PyImport_AddModule("panda3d");
    PyModule_AddStringConstant(panda3d_module, "__package__", "panda3d");
    PyModule_AddObject(panda3d_module, "__path__", PyList_New(0));
    PyObject *sys_modules = PySys_GetObject("modules");

    PyObject *panda3d_dict = PyModule_GetDict(panda3d_module);

    PyObject *core_module = PyInit_core();
    PyDict_SetItemString(panda3d_dict, "core", core_module);
    PyDict_SetItemString(sys_modules, "panda3d.core", core_module);

    PyObject *direct_module = PyInit_direct();
    PyDict_SetItemString(panda3d_dict, "direct", direct_module);
    PyDict_SetItemString(sys_modules, "panda3d.direct", direct_module);

    PyObject *ai_module = PyInit_ai();
    PyDict_SetItemString(panda3d_dict, "ai", direct_module);
    PyDict_SetItemString(sys_modules, "panda3d.ai", ai_module);

    PyObject *physics_module = PyInit_physics();
    PyDict_SetItemString(panda3d_dict, "physics", physics_module);
    PyDict_SetItemString(sys_modules, "panda3d.physics", physics_module);

    init_libOpenALAudio();
    init_libpnmimagetypes();
    init_libwebgldisplay();

    emscripten_set_main_loop(&do_poll, 0, 0);

    if (PyErr_Occurred()) {
        PyErr_Print();
        return 1;
    }

    if (PyImport_ImportFrozenModule("__main__") < 0) {
        PyErr_Print();
        return 1;
    }

    return 0;
}
"""

def _register_python_loaders():
    # We need this method so that we don't depend on direct.showbase.Loader.
    if getattr(_register_python_loaders, 'done', None):
        return

    _register_python_loaders.done = True

    from importlib.metadata import entry_points

    eps = entry_points()
    if isinstance(eps, dict): # Python 3.8 and 3.9
        loaders = eps.get('panda3d.loaders', ())
    else:
        loaders = eps.select(group='panda3d.loaders')

    import panda3d.core as p3d
    registry = p3d.LoaderFileTypeRegistry.get_global_ptr()
    for entry_point in loaders:
        registry.register_deferred_type(entry_point)


def _model_to_bam(srcpath, dstpath, embed_textures=False):
    # Call this when using panda3d-gltf, comment out otherwise
    _register_python_loaders()

    import panda3d.core as p3d
    if dstpath.endswith('.gz') or dstpath.endswith('.pz'):
        dstpath = dstpath[:-3]
    dstpath = dstpath + '.bam'

    src_fn = p3d.Filename.from_os_specific(srcpath)
    dst_fn = p3d.Filename.from_os_specific(dstpath)
    dst_fn.set_binary()

    loader = p3d.Loader.get_global_ptr()
    options = p3d.LoaderOptions(p3d.LoaderOptions.LF_report_errors |
                                p3d.LoaderOptions.LF_no_ram_cache)
    node = loader.load_sync(src_fn, options)
    if not node:
        raise IOError('Failed to load model: %s' % (srcpath))

    stream = p3d.OFileStream()
    if not dst_fn.open_write(stream):
        raise IOError('Failed to open .bam file for writing: %s' % (dstpath))

    # We pass it the source filename here so that texture files are made
    # relative to the original pathname and don't point from the destination
    # back into the source directory.
    dout = p3d.DatagramOutputFile()
    if not dout.open(stream, src_fn) or not dout.write_header("pbj\0\n\r"):
        raise IOError('Failed to write to .bam file: %s' % (dstpath))

    writer = p3d.BamWriter(dout)
    writer.root_node = node
    writer.init()
    if embed_textures:
        writer.set_file_texture_mode(p3d.BamEnums.BTM_rawdata)
    else:
        writer.set_file_texture_mode(p3d.BamEnums.BTM_relative)
    writer.write_object(node)
    writer.flush()
    writer = None
    dout.close()
    dout = None
    stream.close()

for model in CONVERT_MODELS:
    _model_to_bam(THIS_DIR+model, THIS_DIR+model, CONVERT_MODELS_EMBED_TEXTURES)


freezer.moduleSearchPath = [PANDA_BUILT_DIR, PY_STDLIB_DIR, PY_MODULE_DIR]

# Set this to keep the intermediate .c and .o file
#freezer.keepTemporaryFiles = True

freezer.cenv = EmscriptenEnvironment()
freezer.excludeModule('doctest')
freezer.excludeModule('difflib')
freezer.excludeModule('panda3d')
freezer.addModule('__main__', filename=THIS_DIR+r"/main.py")

freezer.done(addStartupModules=True)
freezer.generateCode("TSAVideoGame", compileToExe=True)
