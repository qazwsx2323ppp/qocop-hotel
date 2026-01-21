from pathlib import Path

from tkinter import (
    Frame,
    Canvas,
    Entry,
    StringVar,
    Text,
    Button,
    PhotoImage,
    messagebox,
)
import controller as db_controller

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def normalize_room_no(value):
    text = str(value).strip().upper()
    if not text:
        return None
    if len(text) < 2:
        return None
    if not text[0].isalpha() or not text[1:].isdigit():
        return None
    return text


def add_rooms():
    AddRooms()


class AddRooms(Frame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.data = {"r_no": StringVar(), "type": StringVar(), "price": StringVar()}

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
        self.image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
        image_1 = self.canvas.create_image(137.0, 153.0, image=self.image_image_1)

        self.canvas.create_text(
            52.0,
            128.0,
            anchor="nw",
            text="房间号",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
        entry_bg_1 = self.canvas.create_image(141.5, 165.0, image=self.entry_image_1)
        entry_1 = Entry(
            self,
            textvariable=self.data["r_no"],
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            font=("Montserrat Bold", 18 * -1),
            foreground="#777777",
        )
        entry_1.place(x=52.0, y=153.0, width=179.0, height=22.0)
        self._set_placeholder(entry_1, "例如 A307")

        self.canvas.create_text(
            52.0,
            155.0,
            anchor="nw",
            text="A307",
            fill="#000000",
            font=("Montserrat SemiBold", 17 * -1),
        )

        self.image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
        image_2 = self.canvas.create_image(258.0, 259.0, image=self.image_image_2)

        self.canvas.create_text(
            52.0,
            234.0,
            anchor="nw",
            text="全价",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
        entry_bg_2 = self.canvas.create_image(257.5, 271.0, image=self.entry_image_2)
        entry_2 = Entry(
            self,
            textvariable=self.data["price"],
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            font=("Montserrat Bold", 18 * -1),
            foreground="#777777",
        )
        entry_2.place(x=52.0, y=259.0, width=411.0, height=22.0)

        self.canvas.create_text(
            52.0,
            261.0,
            anchor="nw",
            text="1024",
            fill="#000000",
            font=("Montserrat SemiBold", 17 * -1),
        )

        self.image_image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
        image_3 = self.canvas.create_image(378.0, 153.0, image=self.image_image_3)

        self.canvas.create_text(
            293.0,
            128.0,
            anchor="nw",
            text="类型：(D)豪华/(N)普通",
            fill="#5E95FF",
            font=("Montserrat Bold", 14 * -1),
        )

        self.entry_image_3 = PhotoImage(file=relative_to_assets("entry_3.png"))
        entry_bg_3 = self.canvas.create_image(382.5, 165.0, image=self.entry_image_3)
        entry_3 = Entry(
            self,
            textvariable=self.data["type"],
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0,
            font=("Montserrat Bold", 18 * -1),
            foreground="#777777",
        )
        entry_3.place(x=293.0, y=153.0, width=179.0, height=22.0)

        self.canvas.create_text(
            293.0,
            155.0,
            anchor="nw",
            text="D / N",
            fill="#000000",
            font=("Montserrat SemiBold", 17 * -1),
        )

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
            181.0,
            58.0,
            anchor="nw",
            text="新增房间",
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

    # Save the data to the database
    def save(self):
        # check if any fields are empty
        for val in self.data.values():
            if val.get() == "":
                messagebox.showinfo("错误", "请填写所有字段")
                return

        room_no = normalize_room_no(self.data["r_no"].get())
        if room_no is None:
            messagebox.showerror("错误", "房间号格式应为 A307")
            return
        if not str(self.data["price"].get()).isdigit():
            messagebox.showerror("错误", "价格请输入数字")
            return

        ok, err = db_controller.add_room(
            room_no, *[self.data[label].get() for label in ("price", "type")]
        )

        if ok:
            messagebox.showinfo("成功", "房间添加成功")
            self.parent.navigate("view")
            self.parent.windows.get("view").handle_refresh()
            # clear all fields
            for label in self.data.keys():
                self.data[label].set(0)
        else:
            if err == "duplicate_room_no":
                messagebox.showerror("错误", "房间号已存在，请重新输入")
            else:
                messagebox.showerror("错误", "无法添加房间，请确认数据已校验")

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
