#include "${INCLUDE}" // Import funkcji sterownika

// Wątek aplikacji
void loop(void)
{
  while(1) {
    // Ustawienie diody informacyjnej, aby świeciła na czerwoną
    LED_Set(RGB_Red);
    delay(1000); // Odczekaj 1s
    // Ustawienie diody informacyjnej, aby świeciła na zieloną
    LED_Set(RGB_Green);
    delay(1000); // Odczekaj 1s
    // Ustawienie diody informacyjnej, aby świeciła na niebieską
    LED_Set(RGB_Blue);
    delay(1000); // Odczekaj 1s
    // Wyłączenie diody informacyjnej
    LED_Rst();
    delay(1000); // Odczekaj 1s
  }
}

stack(stack_plc, 256); // Stos pamięci dla wątku PLC
stack(stack_dbg, 256); // Stos pamięci dla wątku debug'era (logs + bash)
stack(stack_loop, 1024); // Stos pamięci dla funkcji loop

int main(void)
{
  thread(PLC_Thread, stack_plc); // Dodanie wątku sterownika
  thread(DBG_Loop, stack_dbg); // Dodanie wątku debug'era (logs + bash)
  thread(loop, stack_loop); // Dodanie funkcji loop jako wątek
  vrts_init(); // Włączenie systemy przełączania wątków VRTS
  while(1); // W to miejsce program nigdy nie powinien dojść
}