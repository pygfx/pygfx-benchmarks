import random

import numpy as np
import pygfx as gfx

from _benchmark import benchmark, run_all


big_text = """
Lorem ipsum odor amet, consectetuer adipiscing elit. Congue aliquet fusce hendrerit leo fames ac. Proin nec sit mauris lobortis quam ultrices. Senectus habitasse ad orci posuere fusce. Ut lectus inceptos commodo taciti porttitor a habitasse. Vulputate tempus ullamcorper aptent molestie vestibulum massa. Tristique nec ac sagittis morbi; egestas nisl donec morbi. Et nisi donec conubia duis rutrum tellus?

Amet praesent proin leo morbi dignissim eu et sagittis. Finibus dictum parturient eleifend in interdum class mauris. Nisi mollis est per; aliquet primis interdum. Semper torquent sem aliquam eleifend id malesuada. Magnis tincidunt suspendisse sapien massa etiam aptent libero morbi. Commodo montes ac torquent quam rutrum. Ante dis potenti nostra maximus non mattis. Interdum fringilla suspendisse parturient accumsan habitant ridiculus proin. Cursus dolor facilisis arcu ultricies facilisi velit habitasse natoque.

Netus libero nascetur senectus habitant viverra cras euismod maximus. Mattis praesent ornare morbi donec commodo. Natoque ante taciti primis habitasse malesuada montes euismod. Quisque id faucibus, condimentum vehicula montes fusce sem. Eu congue malesuada justo a nulla suscipit. Aplatea curabitur et eget felis, at aptent velit. Ultricies id viverra vestibulum eleifend, massa sed nec. Magnis nullam curae urna quam condimentum facilisis eu. Euismod euismod phasellus, tempus inceptos risus accumsan morbi. Curae metus libero volutpat nisi quis facilisi montes.

Netus egestas magnis cras habitasse porta egestas fringilla. Tortor lectus tortor iaculis eu arcu ex sollicitudin quis. Nascetur dis malesuada ad dapibus, lobortis maximus leo inceptos eros. Vel auctor libero iaculis aliquet fringilla leo donec; curabitur eleifend. Quis laoreet placerat cursus dui sapien finibus. Mi gravida dapibus ante libero tristique auctor lobortis. Primis litora vivamus enim blandit sed.

Nisl eleifend ante mus fusce; feugiat habitasse montes? Volutpat convallis ullamcorper viverra quisque neque porttitor sit? Tempus ut ligula ex maximus ultricies justo erat tempus. Risus bibendum malesuada vitae nulla erat fermentum luctus. Viverra enim nisi cursus sodales tortor volutpat eu? Porta libero mauris ligula elementum facilisi fermentum dignissim. Himenaeos convallis nunc viverra ligula litora mauris tempor etiam? Sem accumsan nibh adipiscing proin sagittis hendrerit suscipit dignissim.

Sapien fringilla facilisis nisl neque leo justo natoque quam. Integer vehicula suspendisse vehicula metus hac rhoncus sed. Lectus felis torquent suspendisse ullamcorper sem est tellus habitasse cras. Dictumst justo nunc vitae quisque facilisis. Vitae bibendum habitant semper nullam purus tellus phasellus faucibus. Arcu nascetur penatibus efficitur ridiculus nullam elit. Mauris nostra ridiculus nibh bibendum tempus sollicitudin ipsum non eleifend.

Ultrices himenaeos litora cubilia risus magna hac. Nisi donec sit praesent pellentesque molestie taciti dui. Laoreet tristique odio natoque elementum duis platea posuere. Dolor adipiscing ligula posuere sodales cubilia, taciti condimentum dignissim. Viverra eget class torquent fusce condimentum. Conubia laoreet viverra dictumst habitant, natoque potenti senectus. Sem leo diam suscipit massa faucibus congue. Faucibus cras ad leo pretium augue iaculis ex mus. Quisque malesuada torquent elit curabitur mauris eleifend? Viverra interdum enim dictum curae fringilla potenti felis dolor duis.

Vitae maecenas varius justo egestas eleifend finibus congue. Orci eu taciti sagittis mus nibh congue urna conubia. Habitant duis nec vulputate orci congue quam. Est sem amet nulla blandit eget. Litora ut est lobortis natoque commodo; eros molestie rhoncus. Inceptos commodo lectus ante porttitor primis duis libero inceptos. Ipsum convallis libero torquent mattis etiam sed finibus. Hac leo ligula; dis fames molestie elit. Cras ridiculus euismod sollicitudin sodales nec ante fusce tristique.

Elit curabitur condimentum eros faucibus rhoncus faucibus taciti. Congue enim consequat venenatis torquent ante senectus neque tortor tincidunt. Odio litora nisl pharetra magnis arcu lacus. Vulputate amet velit nascetur arcu sociosqu erat scelerisque. Habitant ipsum dis faucibus eros tempor tellus. Eleifend class ex non consequat nunc conubia et hendrerit ligula. Porttitor vulputate dolor phasellus efficitur nisi viverra. Orci ridiculus senectus sit nostra conubia purus sociosqu mauris. Elementum nisl tristique magnis vulputate enim efficitur. Dignissim phasellus integer quisque dapibus sollicitudin conubia montes risus.

Eleifend imperdiet primis quam conubia sapien lacus nec sagittis curabitur. Dapibus ante laoreet integer euismod sit ad nulla ultricies. Aenean neque libero lacus ut mollis mus? Cubilia nascetur tempus ultrices vel cursus ipsum egestas vivamus varius. Tellus nostra tristique quis ante felis. Per maximus odio eget nisl ornare; faucibus risus natoque. Curae dapibus interdum finibus adipiscing dui duis convallis eleifend. Ligula ornare himenaeos dictumst felis nam tempor tempor. Curae penatibus tortor vel adipiscing quam nec penatibus himenaeos.
"""

@benchmark
def benchmark_large_static_text(canvas):

    renderer = gfx.WgpuRenderer(canvas, blend_mode="ordered1")

    scene = gfx.Scene()

    scene.add(gfx.Background.from_color("#fff"))


    material = gfx.TextMaterial(color="#000")

    tob = gfx.Text(gfx.TextGeometry(text=big_text, max_width=1000), material)
    scene.add(tob)

    camera = gfx.OrthographicCamera(900, 900)
    # camera.show_object(tob)
    renderer.request_draw(lambda: renderer.render(scene, camera))

    # First draw to load stuff in memory
    canvas._draw_frame_and_present()

    yield None

    while True:
        canvas._draw_frame_and_present()  # includes time to take screenshot
        yield  # renderer.stats["gpu_times"]


@benchmark
def benchmark_changing_one_word_in_big_text(canvas):

    renderer = gfx.WgpuRenderer(canvas, blend_mode="ordered1")

    scene = gfx.Scene()

    scene.add(gfx.Background.from_color("#fff"))


    material = gfx.TextMaterial(color="#000")

    tob = gfx.Text(gfx.TextGeometry(text=big_text, max_width=1000), material)
    scene.add(tob)

    camera = gfx.OrthographicCamera(900, 900)
    renderer.request_draw(lambda: renderer.render(scene, camera))

    # First draw to load stuff in memory
    canvas._draw_frame_and_present()

    alt_words = list(set(big_text.split()))

    yield None

    while True:
        new_word = random.choice(alt_words)
        tob.geometry.set_text(big_text.replace("Himenaeos", new_word))
        tob.geometry._on_update_object()
        # canvas._draw_frame_and_present()
        yield


@benchmark
def benchmark_changing_one_word_in_small_text(canvas):

    renderer = gfx.WgpuRenderer(canvas, blend_mode="ordered1")

    scene = gfx.Scene()

    scene.add(gfx.Background.from_color("#fff"))


    material = gfx.TextMaterial(color="#000")

    tob = gfx.Text(gfx.TextGeometry(text="100 fps", max_width=1000), material)
    scene.add(tob)

    camera = gfx.OrthographicCamera(900, 900)
    renderer.request_draw(lambda: renderer.render(scene, camera))

    # First draw to load stuff in memory
    canvas._draw_frame_and_present()

    alt_words = list(set(big_text.split()))

    yield None

    while True:
        new_text = f"{random.randint(10, 500)} fps"
        tob.geometry.set_text(new_text)
        tob.geometry._on_update_object()
        # canvas._draw_frame_and_present()  # include buffer updates
        yield


@benchmark
def multiple_text_objects(canvas):
    yield from benchmark_multi_text(canvas, False)


@benchmark
def multitext_geometry(canvas):
    if not hasattr(gfx, "MultiTextGeometry"):
        while True:
            yield
    else:
        yield from benchmark_multi_text(canvas, True)


def benchmark_multi_text(canvas, use_multi_text):

    renderer = gfx.WgpuRenderer(canvas, blend_mode="ordered1")

    scene = gfx.Scene()

    scene.add(gfx.Background.from_color("#fff"))

    n = 1000
    positions = np.random.uniform(1, 99, (n, 3)).astype(np.float32)

    if use_multi_text:
        text = gfx.Text(
            gfx.MultiTextGeometry(
                anchor="top-left", anchor_offset=2, screen_space=True, font_size=14
            ),
            gfx.TextMaterial(color="#000"),
        )
        scene.add(text)

        text.geometry.set_text_block_count(n)
        text.geometry.positions = gfx.Buffer(positions)
    else:
        material = gfx.TextMaterial(color="#000")
        for i in range(n):
            text = gfx.Text(
                gfx.TextGeometry(
                    anchor="top-left", anchor_offset=2, screen_space=True, font_size=14
                ),
                material,
            )
            scene.add(text)
            text.local.position = positions[i]

    # Set the text of each text block.
    for i in range(n):
        pos = positions[i]
        s = f"({pos[0]:0.0f}, {pos[1]:0.0f}, {pos[2]:0.0f})"
        if use_multi_text:
            t = text.geometry.get_text_block(i)
        else:
            t = scene.children[i + 1].geometry
        t.set_text(s)


    camera = gfx.PerspectiveCamera()
    camera.show_object(scene)

    renderer = gfx.renderers.WgpuRenderer(canvas)
    controller = gfx.OrbitController(camera, register_events=renderer)

    renderer.request_draw(lambda: renderer.render(scene, camera))

    # First draw to load stuff in memory
    canvas._draw_frame_and_present()

    yield None

    while True:
        canvas._draw_frame_and_present()  # includes time to take screenshot
        yield  # renderer.stats["gpu_times"]



if __name__ == "__main__":
    from wgpu.gui.auto import WgpuCanvas

    c = None
    # c = WgpuCanvas()

    run_all(globals(), c)
