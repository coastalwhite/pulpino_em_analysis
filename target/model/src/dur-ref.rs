#![no_main]
#![no_std]

use core::arch::asm;
use core::panic::PanicInfo;

use ext_io::Timer;

#[panic_handler]
fn panic(_: &PanicInfo) -> ! {
    loop {}
}

#[export_name = "_start"]
fn main() {
    ext_io::led(false);

    flush();

    Timer::reset();
    Timer::start();

    unsafe {
        asm!("
            {PROLOGUE}
            nop; nop; nop; nop; nop;
            {TARGET}
            nop; nop; nop; nop; nop;
            {EPILOGUE}
        ", out("t1") _, out("t2") _, out("t3") _, out("t4") _);
    }

    Timer::stop();

    ext_io::write_word(Timer::value());
}

#[inline(always)]
fn flush() {
    for i in 0..128 {
        unsafe {
            ((0x0010_4000 | (i << 4)) as *const u32).read_volatile();
        }
    }
}