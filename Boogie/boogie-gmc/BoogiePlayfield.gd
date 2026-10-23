extends Control
## Photo-based visual starter for the real Allied Leisure Boogie playfield.
## This is a visual reference, not yet a physics simulation or MPF input display.

@export var board_texture: Texture2D

const HOTSPOTS := [
    {"p": Vector2(0.50, 0.16), "label": "100-POINT POP BUMPER", "n": "1"},
    {"p": Vector2(0.50, 0.075), "label": "TOP DROP TARGET BANK", "n": "2"},
    {"p": Vector2(0.27, 0.23), "label": "LEFT SLINGSHOT", "n": "3"},
    {"p": Vector2(0.73, 0.23), "label": "RIGHT SLINGSHOT", "n": "4"},
    {"p": Vector2(0.23, 0.43), "label": "LEFT GATE / TARGET AREA", "n": "5"},
    {"p": Vector2(0.77, 0.43), "label": "RIGHT GATE / TARGET AREA", "n": "6"},
    {"p": Vector2(0.50, 0.68), "label": "DOUBLE BONUS WHEEL", "n": "7"},
    {"p": Vector2(0.37, 0.91), "label": "LEFT FLIPPER", "n": "8"},
    {"p": Vector2(0.63, 0.91), "label": "RIGHT FLIPPER", "n": "9"},
]

var show_hotspots := true
var selected_label := "Select a numbered marker to identify a playfield area"
var board_rect := Rect2()

func _ready() -> void:
    set_process_input(true)
    queue_redraw()

func _draw() -> void:
    var view := get_rect()
    draw_rect(view, Color("10151d"), true)
    # Soft inset frame
    draw_rect(Rect2(Vector2(20, 20), view.size - Vector2(40, 40)), Color("222c39"), true)
    draw_rect(Rect2(Vector2(22, 22), view.size - Vector2(44, 44)), Color("111821"), true)

    var top_margin := 74.0
    var bottom_margin := 76.0
    var max_size := Vector2(view.size.x * 0.70, view.size.y - top_margin - bottom_margin)
    var tex_size := board_texture.get_size() if board_texture else Vector2(760, 1120)
    var scale_factor := minf(max_size.x / tex_size.x, max_size.y / tex_size.y)
    var drawn_size := tex_size * scale_factor
    board_rect = Rect2(Vector2((view.size.x - drawn_size.x) * 0.5, top_margin + (max_size.y - drawn_size.y) * 0.5), drawn_size)

    draw_string(ThemeDB.fallback_font, Vector2(42, 52), "BOOGIE", HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Color("f4c95d"))
    draw_string(ThemeDB.fallback_font, Vector2(185, 50), "ALLIED LEISURE  •  PLAYFIELD REFERENCE", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("c4cedb"))

    if board_texture:
        draw_rect(board_rect.grow(7), Color("d7b16c"), true)
        draw_rect(board_rect.grow(3), Color("07090d"), true)
        draw_texture_rect(board_texture, board_rect, false)

    if show_hotspots:
        for item in HOTSPOTS:
            var center := board_rect.position + Vector2(item.p.x * board_rect.size.x, item.p.y * board_rect.size.y)
            draw_circle(center, 17, Color(0.05, 0.08, 0.12, 0.84))
            draw_circle(center, 15, Color("f4c95d"))
            draw_circle(center, 11, Color("182331"))
            draw_string(ThemeDB.fallback_font, center + Vector2(-4, 5), item.n, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("fff4d2"))

    var panel_x := view.size.x * 0.79
    draw_string(ThemeDB.fallback_font, Vector2(panel_x, 105), "PLAYFIELD AREAS", HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("f4c95d"))
    var y := 139.0
    for item in HOTSPOTS:
        draw_circle(Vector2(panel_x + 8, y - 5), 9, Color("f4c95d"))
        draw_string(ThemeDB.fallback_font, Vector2(panel_x + 5, y - 1), item.n, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("182331"))
        var label_size := 12
        draw_string(ThemeDB.fallback_font, Vector2(panel_x + 24, y), item.label, HORIZONTAL_ALIGNMENT_LEFT, view.size.x - panel_x - 35, label_size, Color("d8e0eb"))
        y += 37

    draw_line(Vector2(38, view.size.y - 61), Vector2(view.size.x - 38, view.size.y - 61), Color("394657"), 1.0)
    draw_string(ThemeDB.fallback_font, Vector2(42, view.size.y - 34), selected_label, HORIZONTAL_ALIGNMENT_LEFT, view.size.x - 84, 14, Color("d8e0eb"))
    draw_string(ThemeDB.fallback_font, Vector2(42, view.size.y - 12), "VISUAL MOCKUP ONLY  •  NO BALL PHYSICS OR MPF INPUTS WIRED YET", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color("9aa7b8"))

func _gui_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        if board_rect.has_point(event.position):
            var local :Vector2 = (event.position - board_rect.position) / board_rect.size
            var best = null
            var best_distance := 999.0
            for item in HOTSPOTS:
                var d :float = local.distance_to(item.p)
                if d < best_distance:
                    best_distance = d
                    best = item
            if best != null and best_distance < 0.08:
                selected_label = "Marker %s: %s" % [best.n, best.label]
            else:
                selected_label = "Playfield photo selected — marker locations are approximate"
            queue_redraw()
