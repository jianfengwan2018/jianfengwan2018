extends Control
# 大化春秋开场：空教室 -> 独白 -> 赠书视频 -> 背包
# 将 1847.mp4 转为 Godot 可播放的 Ogg Theora 文件，放到 res://assets/1847.ogv
var phase := 0
var book_received := false
var dialogue := ["唉……怎么会这样呢？", "真是让人头疼啊……", "嗯？老师来了吗？"]
var label: Label
var bag: Button
var video: VideoStreamPlayer
var student: Label
var elapsed := 0.0
var player_has_video := false

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.color = Color("#d6d0be")
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	for i in range(4):
		var desk := ColorRect.new()
		desk.color = Color("#8a6246")
		desk.position = Vector2(150 + i * 220, 330)
		desk.size = Vector2(155, 50)
		add_child(desk)
	var board := Label.new()
	board.text = "空教室"
	board.position = Vector2(450, 80)
	board.add_theme_font_size_override("font_size", 34)
	add_child(board)
	student = Label.new()
	student.text = "◯\n/|\\\n/ \\"
	student.position = Vector2(550, 240)
	student.add_theme_font_size_override("font_size", 38)
	add_child(student)
	label = Label.new()
	label.position = Vector2(120, 490)
	label.size = Vector2(920, 90)
	label.add_theme_font_size_override("font_size", 26)
	label.text = "主角：（低头，神情苦恼）\n点击画面继续"
	add_child(label)
	bag = Button.new()
	bag.text = "背包"
	bag.position = Vector2(1000, 25)
	bag.size = Vector2(120, 55)
	bag.visible = false
	bag.pressed.connect(_open_bag)
	add_child(bag)
	video = VideoStreamPlayer.new()
	video.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	video.visible = false
	add_child(video)
	video.finished.connect(_finish_video)
	var path := "res://assets/1847.ogv"
	if ResourceLoader.exists(path):
		video.stream = load(path)
		player_has_video = true
	set_process(true)

func _process(delta: float) -> void:
	elapsed += delta
	if phase == 0:
		student.position.y = 240 + sin(elapsed * 1.6) * 2
	if phase == 4:
		bag.modulate = Color(1.0, 0.75 + 0.25 * sin(elapsed * 5.0), 0.4)

func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		_advance()
	elif event is InputEventScreenTouch and event.pressed:
		_advance()

func _advance() -> void:
	if phase == 0:
		phase = 1
		label.text = "主角：" + dialogue[0]
	elif phase == 1:
		phase = 2
		label.text = "主角：" + dialogue[1]
	elif phase == 2:
		phase = 3
		student.text = "◯\n/|\\\n/ \\"
		label.text = "主角：" + dialogue[2]
	elif phase == 3:
		phase = 5
		if player_has_video:
			video.visible = true
			video.play()
		else:
			label.text = "待接入老师赠书视频：assets/1847.ogv\n点击继续（当前仅供测试流程）"
	elif phase == 5 and not player_has_video:
		_finish_video()

func _finish_video() -> void:
	video.stop()
	video.visible = false
	phase = 4
	book_received = true
	bag.visible = true
	label.text = "获得关键道具《大化春秋》！\n点击闪烁的背包查看。"

func _open_bag() -> void:
	if not book_received:
		return
	label.text = "背包：《大化春秋》 ×1\n书上的文字很奇怪，现在还看不懂。\n（解锁事件尚待设计）"
