#!/usr/bin/env python3
from pwn import *

# ---- config ----------------------------------------------------------------
exe = context.binary = ELF("./chall", checksec=False)
libc = ELF("./libc.so.6", checksec=False) if args.LIBC else None
context.log_level = "info"            # set args.DEBUG for debug
HOST, PORT = "TARGET_HOST", 1337      # from current-state.md Allowed targets

GDB_SCRIPT = """
# b *main
# c
"""

def start():
    if args.REMOTE:
        return remote(HOST, PORT)
    if args.GDB:
        return gdb.debug([exe.path], gdbscript=GDB_SCRIPT)
    return process([exe.path])

# ---- helpers ---------------------------------------------------------------
io = start()
s   = lambda d: io.send(d)
sl  = lambda d: io.sendline(d)
sa  = lambda t, d: io.sendafter(t, d)
sla = lambda t, d: io.sendlineafter(t, d)
rl  = lambda: io.recvline()
ru  = lambda t: io.recvuntil(t)

# ---- exploit ---------------------------------------------------------------
# 1) find offset to RIP:  cyclic(200) -> crash -> cyclic_find(leak)
offset = 0

# 2) leak libc (if needed), resolve base
#    leak = u64(io.recvn(6).ljust(8, b"\x00"))
#    libc.address = leak - libc.sym["puts"]

# 3) build chain
rop = ROP(exe)
# rop.raw(rop.find_gadget(["ret"]))     # stack align
# rop.call(exe.plt["puts"], [exe.got["puts"]])
# rop.call(exe.sym["main"])

payload = flat({offset: rop.chain()})
# sla(b"> ", payload)

# 4) grab flag — print ONLY the flag (verifier reads notes.md candidate)
io.interactive()
