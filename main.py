import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Slider, Button


# Передаем привет от Плотникова Кирилла и Власова Сергея Валентине Сморяковой 
def calculate_model(S_val, R_val, C_total_val, u_zi_val):
    """
    S_val: Крутизна (А/В)
    R_val: Сопротивление нагрузки (Ом)
    C_total_val: Суммарная емкость (Фарад)
    u_zi_val: Входное напряжение (В)
    """
    # Константы, которые мы не меняем ползунками
    r_si = 10e3  # Внутреннее сопротивление (10 кОм)
    U_p = 5.0  # Питание (5 В)

    # Временные параметры
    t_end = 50e-9  # 50 наносекунд
    N = 2000
    h = t_end / N
    t = np.linspace(0, t_end, N)

    U_out = np.zeros(N)
    U_out[0] = U_p  # Начальное условие

    # Коэффициент при производной
    K = 1.0 / C_total_val

    # Проводимость цепи
    G_total = (1 / r_si) + (1 / R_val)

    # Решаем методом Эйлера
    for n in range(N - 1):
        # Если напряжение упало до 0, то вообщем то в реале будет 0 а не отрицалтельные значения. Ну то есть кондей пуст.
        if U_out[n] <= 0:
            U_out[n + 1] = 0
            continue

        # Уравнение:
        # I_R (втекает) = (Up - U) / R
        # I_rsi (утекает) = U / r_si
        # I_transistor (утекает) = S * u_zi
        # dU/dt = (1/C) * (I_in - I_out)

        # Ток от источника питания через R
        I_supply = (U_p - U_out[n]) / R_val

        # Ток утечки через r_си
        I_leak = U_out[n] / r_si

        # Ток транзистора
        I_trans = S_val * u_zi_val

        # Сумма токов (с учетом знаков: втекает +, вытекает -)
        Current_sum = I_supply - I_leak - I_trans

        # Производная
        dU_dt = K * Current_sum

        # Шаг
        next_val = U_out[n] + h * dU_dt

        # Ограничение снизу
        U_out[n + 1] = max(0, next_val)

    return t, U_out


# Начальные значения
init_S = 20e-3  # 20 мА/В
init_R = 1000  # 1 кОм
init_C = 72e-12  # 72 пФ
init_uzi = 5.0  # 5 В

fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(left=0.1, bottom=0.35)

t, u = calculate_model(init_S, init_R, init_C, init_uzi)
line, = ax.plot(t * 1e9, u, lw=2, color='blue')

# Настройки осей
ax.set_title("Интерактивная модель инвертора")
ax.set_xlabel("Время, нс")
ax.set_ylabel("Выходное напряжение, В")
ax.set_ylim(-0.5, 6)
ax.set_xlim(0, 50)
ax.grid(True)


axcolor = 'lightgoldenrodyellow'

# Слайдер для S (Крутизна)
ax_S = plt.axes([0.15, 0.25, 0.65, 0.03], facecolor=axcolor)
s_S = Slider(ax_S, 'Крутизна S [мА/В]', 0.1, 50.0, valinit=init_S * 1000)

# Слайдер для R (Сопротивление)
ax_R = plt.axes([0.15, 0.20, 0.65, 0.03], facecolor=axcolor)
s_R = Slider(ax_R, 'Нагрузка R [Ом]', 100, 5000, valinit=init_R)

# Слайдер для C (Емкость)
ax_C = plt.axes([0.15, 0.15, 0.65, 0.03], facecolor=axcolor)
s_C = Slider(ax_C, 'Емкость C [пФ]', 10, 200, valinit=init_C * 1e12)

# Слайдер для U_in (Вход)
ax_U = plt.axes([0.15, 0.10, 0.65, 0.03], facecolor=axcolor)
s_U = Slider(ax_U, 'Вход U_зи [В]', 0.0, 5.0, valinit=init_uzi)



def update(val):
    S_new = s_S.val / 1000.0
    R_new = s_R.val
    C_new = s_C.val * 1e-12
    U_new = s_U.val

    # Пересчитываем модель
    t_new, u_new = calculate_model(S_new, R_new, C_new, U_new)

    # Обновляем график
    line.set_ydata(u_new)
    fig.canvas.draw_idle()


# Привязываем функцию update ко всем слайдерам
s_S.on_changed(update)
s_R.on_changed(update)
s_C.on_changed(update)
s_U.on_changed(update)

resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Сброс', color=axcolor, hovercolor='0.975')


def reset(event):
    s_S.reset()
    s_R.reset()
    s_C.reset()
    s_U.reset()


button.on_clicked(reset)

plt.show()