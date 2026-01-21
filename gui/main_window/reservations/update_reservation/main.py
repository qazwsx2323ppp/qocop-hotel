from pathlib import Path

from tkinter import (
    Frame,
    Canvas,
    Entry,
    Text,
    Button,
    PhotoImage,
    messagebox,
    StringVar,
)
import controller as db_controller

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def normalize_prefixed_id(value, prefix):
    text = str(value).strip() if value is not None else ""
    if not text:
        return None
    if text.startswith(prefix):
        suffix = text[len(prefix) :]
        return text if suffix.isdigit() else None
    return f"{prefix}{text}" if text.isdigit() else None


def update_reservations():
    UpdateReservations()


class ConfirmReservationId(Frame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.data = {"id": StringVar()}

        self.configure(bg="#FFFFFF")

        self.canvas = Canvas(
            self,
            bg="#FFFFFF",
            height=432,
            width=797,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )

        self.canvas.place(x=0, y=0)
        self.canvas.create_rectangle(
            40.0, 14.0, 742.0, 16.0, fill="#EFEFEF", outline=""
        )

        self.canvas.create_text(
            116.0,
            33.0,
            anchor="nw",
            text="ID确认",
            fill="#5E95FF",
            font=("Montserrat Bold", 26 * -1),
        )

        self.canvas.create_text(
            116.0,
            65.0,
            anchor="nw",
            text="请输入预订ID",
            fill="#808080",
            font=("Montserrat SemiBold", 16 * -1),
        )

        self.button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        button_1 = Button(
            self,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.parent.navigate("view"),
            relief="flat",
        )
        button_1.place(x=40.0, y=33.0, width=53.0, height=53.0)

        self.entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
        entry_bg_1 = self.canvas.create_image(391.0, 219.0, image=self.entry_image_1)
        entry_1 = Entry(
            self,
            font=("Montserrat Bold", 18 * -1),
            textvariable=self.data["id"],
            foreground="#777777",
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
        )
        entry_1.place(x=248.0, y=207.0, width=282.0, height=22.0)
        self._set_placeholder(entry_1, "例如 res_1")

        self.button_image_10 = PhotoImage(file=relative_to_assets("button_10.png"))
        button_10 = Button(
            self,
            image=self.button_image_10,
            borderwidth=0,
            highlightthickness=0,
            command=self.handle_confirm,
            relief="flat",
        )
        button_10.place(x=326.0, y=284.0, width=144.0, height=48.0)

    def _set_placeholder(self, entry, value):
        entry.delete(0, "end")
        entry.insert(0, value)
        entry.config(foreground="#AAAAAA")
        entry.bind("<FocusIn>", lambda event: self._clear_placeholder(entry, value))
        entry.bind("<FocusOut>", lambda event: self._restore_placeholder(entry, value))

    def _clear_placeholder(self, entry, value):
        if entry.get() == value:
            entry.delete(0, "end")
            entry.config(foreground="#777777")

    def _restore_placeholder(self, entry, value):
        if entry.get().strip() == "":
            entry.insert(0, value)
            entry.config(foreground="#AAAAAA")

    def reset(self):
        self.data["id"].set("")

    def handle_confirm(self):
        raw_id = self.data["id"].get().strip()
        if raw_id == "例如 res_1":
            raw_id = ""
        reservation_id = normalize_prefixed_id(raw_id, "res_")
        self.parent.reservation_data = db_controller.get_reservations()
        if not reservation_id:
            messagebox.showerror("错误", "请输入正确ID")
            return
        if not any(str(row[0]) == reservation_id for row in self.parent.reservation_data):
            messagebox.showerror("错误", "请输入正确ID")
            return
        self.parent.selected_rid = reservation_id
        self.parent.windows["edit"].initialize()
        self.parent.navigate("edit")


class UpdateReservations(Frame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.selected_r_id = self.parent.selected_rid

        self.configure(bg="#FFFFFF")

        self.data = {
            "id": StringVar(),
            "status": StringVar(),
            "g_id": StringVar(),
            "check_in": StringVar(),
            "room_id": StringVar(),
            "reservation_date": StringVar(),
            "check_out": StringVar(),
        }

        self.initialize()

        self.canvas = Canvas(
            self,
            bg="#FFFFFF",
            height=432,
            width=797,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )

        self.canvas.place(x=0, y=0)
        self.canvas.create_rectangle(
            40.0, 14.0, 742.0, 16.0, fill="#EFEFEF", outline=""
        )

        self.canvas.create_text(
            116.0,
            33.0,
            anchor="nw",
            text="更新预订",
            fill="#5E95FF",
            font=("Montserrat Bold", 26 * -1),
        )

        self.canvas.create_text(
            116.0,
            65.0,
            anchor="nw",
            text="修改信息",
            fill="#808080",
            font=("Montserrat SemiBold", 16 * -1),
        )

        self.button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        button_1 = Button(
            self,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.parent.navigate("add"),
            relief="flat",
        )
        button_1.place(x=40.0, y=33.0, width=53.0, height=53.0)

        self.image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
        image_1 = self.canvas.create_image(145.0, 150.0, image=self.image_image_1)

        self.canvas.create_text(
            60.0,
            125.0,
            anchor="nw",
            text="预订ID",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.id_text = self.canvas.create_text(
            60.0,
            152.0,
            anchor="nw",
            text="请先选择记录...",
            fill="#979797",
            font=("Montserrat Bold", 18 * -1),
        )

        self.image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
        image_2 = self.canvas.create_image(145.0, 246.0, image=self.image_image_2)

        self.canvas.create_text(
            60.0,
            221.0,
            anchor="nw",
            text="",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.image_image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
        image_3 = self.canvas.create_image(145.0, 342.0, image=self.image_image_3)

        self.canvas.create_text(
            60.0,
            317.0,
            anchor="nw",
            text="状态",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
        entry_bg_2 = self.canvas.create_image(149.5, 354.0, image=self.entry_image_2)
        entry_3 = Entry(
            self,
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            font=("Montserrat Bold", 18 * -1),
            foreground="#777777",
            textvariable=self.data["status"],
        )
        entry_3.place(x=60.0, y=342.0, width=179.0, height=22.0)

        self.image_image_4 = PhotoImage(file=relative_to_assets("image_4.png"))
        image_4 = self.canvas.create_image(391.0, 150.0, image=self.image_image_4)

        self.canvas.create_text(
            306.0,
            125.0,
            anchor="nw",
            text="住客ID",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_3 = PhotoImage(file=relative_to_assets("entry_2.png"))
        entry_bg_3 = self.canvas.create_image(395.5, 162.0, image=self.entry_image_3)
        entry_4 = Entry(
            self,
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            font=("Montserrat Bold", 18 * -1),
            foreground="#777777",
            textvariable=self.data["g_id"],
        )
        entry_4.place(x=306.0, y=150.0, width=179.0, height=22.0)
        self._set_placeholder(entry_4, "例如 guest_1")

        self.image_image_5 = PhotoImage(file=relative_to_assets("image_5.png"))
        image_5 = self.canvas.create_image(391.0, 246.0, image=self.image_image_5)

        self.canvas.create_text(
            306.0,
            221.0,
            anchor="nw",
            text="入住时间",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_4 = PhotoImage(file=relative_to_assets("entry_2.png"))
        entry_bg_4 = self.canvas.create_image(395.5, 258.0, image=self.entry_image_4)
        entry_5 = Entry(
            self,
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            font=("Montserrat Bold", 18 * -1),
            foreground="#777777",
            textvariable=self.data["check_in"],
        )
        entry_5.place(x=306.0, y=246.0, width=179.0, height=22.0)

        self.image_image_6 = PhotoImage(file=relative_to_assets("image_6.png"))
        image_6 = self.canvas.create_image(391.0, 342.0, image=self.image_image_6)

        self.canvas.create_text(
            306.0,
            317.0,
            anchor="nw",
            text="预订日期",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_5 = PhotoImage(file=relative_to_assets("entry_2.png"))
        entry_bg_5 = self.canvas.create_image(395.5, 354.0, image=self.entry_image_5)
        entry_6 = Entry(
            self,
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            font=("Montserrat Bold", 18 * -1),
            foreground="#777777",
            textvariable=self.data["reservation_date"],
        )
        entry_6.place(x=306.0, y=342.0, width=179.0, height=22.0)

        self.image_image_7 = PhotoImage(file=relative_to_assets("image_7.png"))
        image_7 = self.canvas.create_image(637.0, 150.0, image=self.image_image_7)

        self.canvas.create_text(
            552.0,
            125.0,
            anchor="nw",
            text="房间ID",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_6 = PhotoImage(file=relative_to_assets("entry_2.png"))
        entry_bg_6 = self.canvas.create_image(641.5, 162.0, image=self.entry_image_6)
        entry_7 = Entry(
            self,
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            font=("Montserrat Bold", 18 * -1),
            foreground="#777777",
            textvariable=self.data["room_id"],
        )
        entry_7.place(x=552.0, y=150.0, width=179.0, height=22.0)
        self._set_placeholder(entry_7, "例如 room_1")

        self.image_image_8 = PhotoImage(file=relative_to_assets("image_8.png"))
        image_8 = self.canvas.create_image(637.0, 246.0, image=self.image_image_8)

        self.canvas.create_text(
            552.0,
            221.0,
            anchor="nw",
            text="退房时间",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_7 = PhotoImage(file=relative_to_assets("entry_2.png"))
        entry_bg_7 = self.canvas.create_image(641.5, 258.0, image=self.entry_image_7)
        entry_8 = Entry(
            self,
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            font=("Montserrat Bold", 18 * -1),
            foreground="#777777",
            textvariable=self.data["check_out"],
        )
        entry_8.place(x=552.0, y=246.0, width=179.0, height=22.0)

        self.button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
        button_2 = Button(
            self,
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.handle_update,
            relief="flat",
        )
        button_2.place(x=570.0, y=318.0, width=144.0, height=48.0)

    def initialize(self):
        self.selected_r_id = self.parent.selected_rid
        self.reservation_data = self.parent.reservation_data

        # Filter out all reservations for selected id reservation
        self.selected_reservation_data = list(
            filter(lambda x: str(x[0]) == self.selected_r_id, self.reservation_data)
        )

        if self.selected_reservation_data:
            self.selected_reservation_data = self.selected_reservation_data[0]
            self._original_room_id = str(self.selected_reservation_data[2])

            self.canvas.itemconfigure(
                self.id_text, text=self.selected_reservation_data[0]
            )
            self.data["g_id"].set(self.selected_reservation_data[1])
            self.data["room_id"].set(self.selected_reservation_data[2])
            self.data["check_in"].set(self.selected_reservation_data[3])
            self.data["check_out"].set(self.selected_reservation_data[4])
            self.data["reservation_date"].set(self.selected_reservation_data[3])
            if len(self.selected_reservation_data) > 5:
                self.data["status"].set(self.selected_reservation_data[5])

    def handle_update(self):

        g_id = normalize_prefixed_id(self.data["g_id"].get(), "guest_")
        room_id = normalize_prefixed_id(self.data["room_id"].get(), "room_")
        if g_id is None or room_id is None:
            messagebox.showerror("错误", "请输入正确ID")
            return
        if getattr(self, "_original_room_id", None) and str(room_id) != str(self._original_room_id):
            if not db_controller.room_is_available(room_id):
                messagebox.showerror("错误", "该房间当前不可预订，请选择可预订房间")
                return

        data = [
            x
            for x in [
                g_id,
                self.data["check_in"].get(),
                room_id,
                self.data["check_out"].get(),
            ]
        ]

        status_input = self.data["status"].get().strip()
        allowed_status = {"", "已预订", "进行中", "已结束", "取消", "已取消"}
        if status_input not in allowed_status:
            messagebox.showerror("错误", "请输入正确状态")
            return

        # Update data and show alert
        if db_controller.update_reservation(self.selected_r_id, *data):
            if status_input in ("取消", "已取消"):
                db_controller.update_reservation_status(self.selected_r_id, "取消")
            messagebox.showinfo("成功", "预订更新成功")
            self.parent.navigate("view")

            self.reset()

        else:
            messagebox.showerror(
                "错误", "更新预订失败：请确认ID存在、日期格式正确且房间可预订"
            )

        self.parent.refresh_entries()
    def reset(self):
        # clear all entries
        for label in self.data:
            self.data[label].set("")

        self.canvas.itemconfigure(
            self.id_text, text="请先选择记录..."
        )

    def _set_placeholder(self, entry, value):
        if entry.get().strip():
            return
        entry.delete(0, "end")
        entry.insert(0, value)
        entry.config(foreground="#AAAAAA")
        entry.bind("<FocusIn>", lambda event: self._clear_placeholder(entry, value))
        entry.bind("<FocusOut>", lambda event: self._restore_placeholder(entry, value))

    def _clear_placeholder(self, entry, value):
        if entry.get() == value:
            entry.delete(0, "end")
            entry.config(foreground="#777777")

    def _restore_placeholder(self, entry, value):
        if entry.get().strip() == "":
            entry.insert(0, value)
            entry.config(foreground="#AAAAAA")
