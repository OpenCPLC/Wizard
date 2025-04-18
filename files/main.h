/**
 * @name  Projekt: ${NAME}
 * @brief Podstawowe informacje projektowe '#define PRO_x'.
 *        Informacje te są wykorzystywane przez program wizard podczas ładowania projektu.
 *        Nie należy ich usuwać, jednak można je edytować.
 *        Zmiana tych parametrów wymaga ponownego wywołania programu Wizard.
 * @date  ${DATE}
 */

#ifndef PRO_x
#define PRO_x

#define PRO_BOARD_${BOARD}
#define PRO_CHIP_${CHIP}
#define PRO_VERSION         "${PROJECT_VERSION}"
#define PRO_USER_MEMORY_KB  ${USER_MEMORY}
#define PRO_OPT_LEVEL       "${OPT_LEVEL}"

#endif

/**
 * @brief W tym pliku należy umieścić parametry konfiguracyjne '#define', które chce się nadpisać.
 * @note  Wiele z bibliotek załącza ten plik '#include', zatem musi on istnieć, nawet jeśli będzie pusty.
 *        Dzięki takiemu rozwiązaniu można nadpisać różnego rodzaju definicje (zmienne) konfiguracyjne.
 *        Biblioteki w pierwszej kolejności będą pobierały definicje zawarte tutaj,
 *        zamiast korzystać z domyślnych wartości zawartych we własnych plikach nagłówkowych '.h'.
 *        Ten mechanizm można również zastosować w swoich projektach, używając dyrektyw warunkowych #ifndef
 *        i dołączając plik main.h w celu nadpisania domyślnych definicji.​
 */

#define LOG_LEVEL       ${LOG_LEVEL}
#define SYS_CLOCK_FREQ  ${FREQ}