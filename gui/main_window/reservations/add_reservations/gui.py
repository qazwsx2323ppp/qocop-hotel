from pathlib import Path

from tkinter import Frame, Canvas, Entry, Text, Button, PhotoImage, messagebox
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


def add_reservations():
    AddReservations()


class AddReservations(Frame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.data = {"g_id": "", "check_in": "", "check_out": "", "r_id": ""}
        self._placeholder_guest = "例如 guest_1"
        self._placeholder_room = "例如 room_1"

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
        self.entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
        entry_bg_1 = self.canvas.create_image(137.5, 153.0, image=self.entry_image_1)

        self.canvas.create_text(
            52.0,
            128.0,
            anchor="nw",
            text="住客ID",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
        entry_bg_2 = self.canvas.create_image(141.5, 165.0, image=self.entry_image_2)
        entry_2 = Entry(
            self,
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            font=("Montserrat Bold", 18 * -1),
            foreground="#777777",
        )
        entry_2.place(x=52.0, y=153.0, width=179.0, height=22.0)
        self.data["g_id"] = entry_2
        self._set_placeholder(entry_2, self._placeholder_guest)

        self.entry_image_3 = PhotoImage(file=relative_to_assets("entry_3.png"))
        entry_bg_3 = self.canvas.create_image(137.5, 259.0, image=self.entry_image_3)

        self.canvas.create_text(
            52.0,
            234.0,
            anchor="nw",
            text="入住时间（如：2026-01-18）",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_4 = PhotoImage(file=relative_to_assets("entry_4.png"))
        entry_bg_4 = self.canvas.create_image(141.5, 271.0, image=self.entry_image_4)
        entry_4 = Entry(
            self,
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            font=("Montserrat Bold", 18 * -1),
            foreground="#777777",
        )
        entry_4.place(x=52.0, y=259.0, width=179.0, height=22.0)
        self.data["check_in"] = entry_4

        self.entry_image_5 = PhotoImage(file=relative_to_assets("entry_5.png"))
        entry_bg_5 = self.canvas.create_image(378.5, 153.0, image=self.entry_image_5)

        self.canvas.create_text(
            293.0,
            128.0,
            anchor="nw",
            text="房间ID",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_6 = PhotoImage(file=relative_to_assets("entry_6.png"))
        entry_bg_6 = self.canvas.create_image(382.5, 165.0, image=self.entry_image_6)
        entry_6 = Entry(
            self,
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            foreground="#777777",
            font=("Montserrat Bold", 18 * -1),
        )
        entry_6.place(x=293.0, y=153.0, width=179.0, height=22.0)
        self.data["r_id"] = entry_6
        self._set_placeholder(entry_6, self._placeholder_room)

        self.entry_image_7 = PhotoImage(file=relative_to_assets("entry_7.png"))
        entry_bg_7 = self.canvas.create_image(378.5, 259.0, image=self.entry_image_7)

        self.canvas.create_text(
            293.0,
            234.0,
            anchor="nw",
            text="退房时间（如：2026-03-06）",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_8 = PhotoImage(file=relative_to_assets("entry_8.png"))
        entry_bg_8 = self.canvas.create_image(382.5, 271.0, image=self.entry_image_8)
        entry_8 = Entry(
            self,
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            foreground="#777777",
            font=("Montserrat Bold", 18 * -1),
        )
        entry_8.place(x=293.0, y=259.0, width=179.0, height=22.0)
        self.data["check_out"] = entry_8

        self.button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        button_1 = Button(
            self,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.save,
            relief="flat",
        )
        button_1.place(x=164.0, y=322.0, width=190.0, height=48.0)

        self.canvas.create_text(
            139.0,
            59.0,
            anchor="nw",
            text="新增预订",
            fill="#5E95FF",
            font=("Montserrat Bold", 26 * -1),
        )

        self.canvas.create_text(
            549.0,
            59.0,
            anchor="nw",
            text="操作",
            fill="#5E95FF",
            font=("Montserrat Bold", 26 * -1),
        )

        self.canvas.create_rectangle(
            515.0, 59.0, 517.0, 370.0, fill="#EFEFEF", outline=""
        )

        self.button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
        button_2 = Button(
            self,
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.parent.navigate("view"),
            relief="flat",
        )
        button_2.place(x=547.0, y=116.0, width=209.0, height=74.0)

        self.button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
        button_3 = Button(
            self,
            image=self.button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.parent.navigate("confirm"),
            relief="flat",
        )
        button_3.place(x=547.0, y=210.0, width=209.0, height=74.0)
        # Set default value for entry
        self.data["check_in"].insert(0, "now")
        self.data["check_out"].insert(0, "now")

    # Save the data to the database
    def save(self):
        # Normalize placeholders
        if self.data["g_id"].get().strip() == self._placeholder_guest:
            self.data["g_id"].delete(0, "end")
        if self.data["r_id"].get().strip() == self._placeholder_room:
            self.data["r_id"].delete(0, "end")

        # check if any fields are empty
        for label in self.data.keys():
            if self.data[label].get() == "":
                messagebox.showinfo("错误", "请填写所有字段")
                return

        g_id = normalize_prefixed_id(self.data["g_id"].get(), "guest_")
        r_id = normalize_prefixed_id(self.data["r_id"].get(), "room_")
        if g_id is None or r_id is None:
            messagebox.showerror("错误", "请输入正确ID")
            return

        # Save the reservation
        ok, err = db_controller.add_reservation(
            g_id, r_id, self.data["check_in"].get(), self.data["check_out"].get()
        )

        if ok:
            messagebox.showinfo("成功", "预订添加成功")
            self.parent.navigate("view")
            self.parent.refresh_entries()

            # clear all fields
            for label in self.data.keys():
                self.data[label].delete(0, "end")
        else:
            if err == "guest_not_found":
                messagebox.showerror("错误", "住客ID不存在，请重新输入")
            elif err == "room_not_found":
                messagebox.showerror("错误", "房间ID不存在，请重新输入")
            elif err == "room_unavailable":
                messagebox.showerror("错误", "该房间当前不可预订，请选择可预订房间")
            elif err in ("invalid_check_in", "invalid_check_out"):
                messagebox.showerror("错误", "日期格式错误，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS")
            elif err == "invalid_date_range":
                messagebox.showerror("错误", "退房时间不能早于入住时间")
            else:
                messagebox.showerror("错误", "无法添加预订，请确认数据已校验")

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
