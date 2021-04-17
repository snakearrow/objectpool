from dearpygui import core, simple
from DetailsWindow import DetailsWindow
import threading
import psutil
import os


class UI:

    def __init__(self, title: str, pools):
        self._render_update_cnt = 0
        self._pools = pools
        self._ui_dirty = False
        self._pid = process = psutil.Process(os.getpid())
        self._title = title
        self._details_windows = []
        
    def destroy(self):
        self._reset()
        core.set_render_callback(None)
        core.stop_dearpygui()

    def _reset(self):
        core.delete_item(f"Object Pool: {self._title}")
        
    def _get_table_data(self, pool):
        data = []
        for obj_id, lst in pool.get_queue().items():
            data.append([lst[-1], str(len(lst))])
        return data
        
    def _show_object_details(self, sender, data):
        entry = data[0]
        pool_name = data[1]
        details_win = DetailsWindow(entry, pool_name, self._hide_object_details)
        self._details_windows.append(details_win)
        details_win.show()
            
    def _hide_object_details(self, sender):
        for win in list(self._details_windows):
            if win.get_name() == sender:
                core.delete_item(sender)
                self._details_windows.remove(win)

    def _render_callback(self, sender, data):
        self._render_update_cnt += 1

        if self._render_update_cnt % 20 == 0:
            self._render_update_cnt = 0
                
            # fields that are most probably always updated
            for pool_name, pool in self._pools.items():
                max_size = str(pool.get_max_size()) if pool.get_max_size() else "inf"
                core.set_value(f"Objects_{pool_name}##total", str(pool.length()) + " / " + max_size)
                core.set_value(f"Objects_{pool_name}##subscribers", str(pool.n_subscriptions()))
                # update table
                if core.does_item_exist(f"Objects_{pool_name}##table"):
                    table_data = self._get_table_data(pool)
                    for entry in table_data:
                        obj_name = entry[0].get_object_name()
                        n_objs = entry[1]
                        btn_name = f"Button_{pool_name}_{obj_name}"
                        if not core.does_item_exist(btn_name):
                            core.add_button(btn_name, label=f"{obj_name} :\t{n_objs}", width=200, parent=f"Objects_{pool_name}##table", callback=self._show_object_details, callback_data=(entry[0], pool_name))
                        else:
                            simple.set_item_label(btn_name, f"{obj_name} :\t{n_objs}")

                # update details window
                for win in self._details_windows:
                    if win.get_pool_name() == pool_name:
                        for obj_id, lst in pool.get_queue().items():
                            if obj_id == win.get_obj_id():
                                win.update(lst[-1])
                                continue
                    win.update_static()
                
            mem_usage_mb = self._pid.memory_info().rss / 1000.0 / 1000.0
            core.set_value("Pools##memory", "{:.2f}".format(mem_usage_mb))
            core.set_value("Pools##cpu", "{:.2f}".format(self._pid.cpu_percent()))

            if not self._ui_dirty:
                return

            # rebuild UI
            self._ui_dirty = False
            self._reset()
            self._build()

    def _show_ui_thread(self):
        core.start_dearpygui()

    def _build(self):
        with simple.window(f"Object Pool: {self._title}", width=600, height=400, x_pos=0, y_pos=0, on_close=self.destroy, no_resize=False, no_close=True, no_move=True, no_collapse=True):
            core.add_label_text("Pools##total", label="Total Pools", default_value=str(len(self._pools)))
            core.add_label_text("Pools##memory", label="Memory Usage (MB)", default_value="0")
            core.add_label_text("Pools##cpu", label="System Load (%)", default_value="0")
            
            # show all pools
            for pool_name, pool in self._pools.items():
                with simple.collapsing_header(f"Pool: {pool_name}", default_open=False):
                    core.add_label_text(f"Objects_{pool_name}##total", label="Total Objects", default_value="0 / inf")
                    core.add_label_text(f"Objects_{pool_name}##subscribers", label="Subscriptions", default_value="0")
                    core.add_indent()
                    with simple.collapsing_header(f"Objects_{pool_name}##table", default_open=True):
                        pass
                    core.unindent()

        core.set_render_callback(self._render_callback)
        core.set_main_window_size(600, 400)
        core.set_main_window_title("Object Pool UI")


    def show(self):
        self._build()
        t = threading.Thread(target=self._show_ui_thread)
        t.start()
        
    def mark_dirty(self):
        self._ui_dirty = True
        
    def update(self, pools):
        self._pools = pools

