#include "rtc.h"
#include "sys.h"
#include "vrts.h"
#include "dbg.h"
#include "main.h"

//------------------------------------------------------------------------------------------------- dbg

UART_t dbg_uart = {
  .reg = USART1,
  .tx_pin = UART1_TX_PC4,
  .rx_pin = UART1_RX_PC5,
  .dma_nbr = DMA_Nbr_4,
  .int_prioryty = INT_Prioryty_Low,
  .UART_115200
};

//------------------------------------------------------------------------------------------------- app

GPIO_t led = { // Nucleo LED
  .port = GPIOA,
  .pin = 5,
  .mode = GPIO_Mode_Output
}; 

void loop(void)
{
  GPIO_Init(&led); // Inicjalizacja diody LED
  while(1) {
    GPIO_Tgl(&led); // Zmiana stanu diody
    LOG_Info("Do nothing"); // Wyświetl wiadomość w pętli
    delay(1000); // Odczekaj 1s
  }
}

//------------------------------------------------------------------------------------------------- main

stack(stack_dbg, 256); // Stos pamięci dla wątku debug'era (logs + bash)
stack(stack_loop, 256); // Stos pamięci dla funkcji loop

int main(void)
{
  system_clock_init(); // Konfiguracja systemowego sygnału zegarowego
  systick_init(10); // Uruchomienie zegara systemowego z dokładnością do 10ms
  RTC_Init(); // Włączenie zegara czasu rzeczywistego (RTC)
  DBG_Init(&dbg_uart); // Inicjalizacja debuger'a (logs + bash)
  DBG_Enter();
  LOG_Init("Hello ${FAMILY} template project", PRO_VERSION);
  thread(DBG_Loop, stack_dbg); // Dodanie wątku debug'era (logs + bash)
  thread(loop, stack_loop); // Dodanie funkcji loop jako wątek
  vrts_init(); // Włączenie systemy przełączania wątków VRTS
  while(1); // W to miejsce program nigdy nie powinien dojść
}