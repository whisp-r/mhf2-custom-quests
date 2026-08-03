.psp

sceIoOpen		equ	0x088E542C
sceIoLseek		equ	0x088E5434
sceIoRead		equ	0x088E53FC
sceIoClose		equ	0x088E5414
sceKDWIA		equ	0x088E5634 ; sceKernelDcacheWritebackInvalidateAll

SLOT_1			equ	0x09623070
SLOT_SIZE		equ	0x6800

SLTI_V0_S3		equ	0x09946B60
SLTI_V0_S1		equ 0x09947BE4

RETURN_VALID	equ	0x09947B6C
RETURN_INVALID	equ 0x09947B64

SP_EVENT_PAGE	equ 0x099B7FC4

.createfile "./build/EventLoaderJPN.bin", 0x8802000
		move	s6, ra
		; Backup registers v0 and s0
		addiu	sp, sp, -12
		sw		s0, 0x8(sp)
		sw		a0, 0x4(sp)
		sw		a1, 0x0(sp)
		; Check if init
		lui		t0, 0x0800
		bgt		s1, t0, OPEN_EVENT_BIN
		nop
		
	CHECK_PAGE:
		la		t0, SP_EVENT_PAGE
		lh		t0, 0x0(t0)
		addi	t0, t0, -0xEA61
		andi	t0, t0, 0xFFFF
		beq		t0, s1, OPEN_EVENT_BIN
		nop
		j		RESTORE_VALID
		nop
		
	OPEN_EVENT_BIN:
		; Open quests file
		la		a0, QUESTS_BIN
		li		a1, 0x1
		jal		sceIoOpen
		li		a2, 0x0
		; Check if file exists
		li		v1, 0x80010002
		beq		v0, v1, NoFile ; Return - no event quests found
		nop
		la		a0, QUESTS_BIN_EXIST
		li		a1, 1
		sw		a1, 0x0(a0)
		li 		v1, 0x0
		move	s0, v0	
		; Get number of pages
		move 	a0, s0
		li		a1, 0x0
		li		a2, 0x0
		li		a3, 0x0
		jal		sceIoLseek ; Get file size
		li		t0, 0x2
		beq		v0, zero, NoFile ; Return - empty file 
		li		a0, 0x6800
		div		v0, a0
		mflo	a0 ; Page num
		li		t0, 0x32 ; Max 50 pages
		bge		a0, t0, clamp_pages
		nop
		j		end_clamp_pages
		nop
	clamp_pages:
		move	a0, t0
	end_clamp_pages:
		li		t0, 0x2A620000
		addu	t0, t0, a0
		sw		t0, SLTI_V0_S3 ; slti v0,s3,pages
		li		t0, 0x2A220000
		addu	t0, t0, a0
		sw		t0, SLTI_V0_S1 ; slti v0,s1,pages
		; Correct offset to load quest
		lw		a2, 0x0(sp)
		li		t0, SLOT_1
		sub		a2, a2, t0
		li		t0, 0x6810
		div		a2, t0
		mflo	a2
		li		t0, 0x6800
		mult	a2, t0
		mflo	a2
		; Seek to offset in file
		move 	a0, s0
		li		a1, 0x0
		li		a3, 0x0
		jal		sceIoLseek
		li		t0, 0x0
		; Read from offset into quest slot
		move	a0, s0
		li		a1, SLOT_1
		jal		sceIoRead
		li		a2, SLOT_SIZE
		; Close quests file
		jal		sceIoClose
		move 	a0, s0
		jal		sceKDWIA
		nop
		; Restore registers backup and return
	RESTORE_VALID:
		jal		Restore
		nop
		move	ra, s6
		j		RETURN_VALID ; Jump back
		sw		a1, 0x78(a0)
		
		Restore:
			; Restore a0 and set a1 to Quest Slot 1
			la		a1, QUESTS_BIN_EXIST
			lw		a1, 0x0(a1)
			beq		a1, zero, SET_QUEST_SLOT
			lw		a1, 0x0(sp)
			li		a1, SLOT_1
		SET_QUEST_SLOT:	
			lw		a0, 0x4(sp)
			lw		s0, 0x8(sp)
			addiu	sp, sp, 12
			jr		ra
			nop
		
		NoFile:
			li		t0, 0x2A620006
			sw		t0, SLTI_V0_S3
			li		t0, 0x2A220006
			sw		t0, SLTI_V0_S1
			la		a0, QUESTS_BIN_EXIST
			sw		zero, 0x0(a0)
			jal		Restore
			nop
			move	ra, s6
			lw		v0, 0x0(a1)
			bnel	v0, zero, NoFileValid
			sw		a1, 0x78(a0)
			j		RETURN_INVALID;
			nop
			
		NoFileValid:
			j		RETURN_VALID;
			nop
		
		QUESTS_BIN:
			.ascii "ms0:/PSP/SAVEDATA/MHF2QST/EVENT.BIN"
			.align 0x4
			
		QUESTS_BIN_EXIST:
			; Empty space
			
	.close