#!/usr/bin/python

'''
def sec():
	with open("section_ip.txt", "r") as f:
		next = 0
		for line in f:
			#fields = line.split();
			info = line[7:40]
			off = line[50:57]
			sz = line[57:64]
			print info,
			if int(off,16) != next:
				print "*",
			else:
				print " ",
			print off, sz,

			next = int(off, 16) + int(sz, 16)
			print "(%s)" % hex(next)
'''

import struct
import sys
import os
import io
import traceback

ELF_MAGIC = '\x7f\x45\x4c\x46'

# Segment Types (Program header types)
PT_NULL = 0
PT_LOAD = 1
PT_DYNAMIC = 2
PT_INTERP  = 3
PT_NOTE    = 4
PT_SHLIB   = 5
PT_PHDR    = 6

# Section Types
SHT_NULL = 0
SHT_PROGBITS = 1
SHT_SYMTAB = 2
SHT_STRTAB = 3
SHT_RELA   = 4
SHT_HASH   = 5
SHT_DYNAMIC= 6
SHT_NOTE   = 7
SHT_NOBITS = 8
SHT_REL    = 9
SHT_SHLIB  = 10
SHT_DYNSYM = 11
SHT_INIT_ARRAY = 14
SHT_FINI_ARRAY = 15

# DT types parsed in android linker
DT_HASH   = 4		# symbol hash talbe
DT_STRTAB = 5		# string table
DT_SYMTAB = 6		# symbol table
DT_PLTREL = 20		# type of relocation entry to which the procedure linkage table refers, DT_REL or DT_RELA
DT_JMPREL	= 23	# PLT relocations only (dynamic linker can ignore if lazy binding), must /w DT_PLTRELSZ, DT_PLTREL
DT_PLTRELSZ	= 2		# size of the PLT relocations, in bytes. must /w DT_JMPREL
DT_REL 	  = 17		# relocation table, must /w DT_RELSZ, DT_RELENT
DT_RELSZ  = 18		# size of the DT_REL, in bytes
DT_PLTGOT = 3		# address of _GLOBAL_OFFSET_TABLE_
DT_DEBUG  = 21
DT_RELA   = 7
DT_INIT   = 12
DT_FINI   = 13
DT_INIT_ARRAY = 25
DT_INIT_ARRAYSZ = 27
DT_FINI_ARRAY = 26
DT_FINI_ARRAYSZ = 28
DT_PREINIT_ARRAY = 32
DT_PREINIT_ARRAYSZ = 33
DT_TEXTREL = 22
DT_SYMBOLIC = 16
DT_NEEDED = 1
# DT_FLAGS  =
DT_STRSZ  = 10
DT_SYMENT = 11

try:
	from awesome_print import ap as pp
except:
	from pprint import pprint as pp

def SearchGotEnd(data, start, end, rels):
	for i in range(end, start, -1):
		num = struct.unpack('<I', data[i - 4 : i])
		for j in range(len(rels)):
			if num == rels[j].r_offset:
				return i
	return 0
	
def SearchPltStart(data):
	return data.find('\x04\xE0\x2D\xE5\x04\xE0\x9F\xE5\x0E\xE0\x8F\xE0\x08\xF0\xBE\xE5')
	
def SearchTextEnd(data):
	return data.find('\x08\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00Android')
	
def SearchRODATA(data, start, end):
	ret_start = -1
	ret_len	= -1
	for i in range(end - start):
		if data[start + i].isalnum():
			ret_start = start + i
			break;
	if ret_start == -1:
		return [ret_start, ret_len]
	'''
	current = ret_start
	while(current < end):
		if not data[current].isalnum():
			hitEndding = True
			for i in range(24):
				if data[current + i].isalnum():
					hitEndding = False
					break;
			if hitEndding:
				ret_len = current - ret_start
				break;
		current = current + 1
	'''
	return [ret_start & ~0x3, (ret_len + 0x3) & ~0x3]

def dict_search_safe(dictionary, key):
		try:
			return dictionary[key]
		except KeyError as e:
			return "(%s)" % hex(key)

class RelInfo:
	def __init__(self, name, r_offset, is_fun):
		self.name = name
		self.r_offset = r_offset
		self.is_fun = is_fun

class Section:
	def __init__(self, name, vaddr, vend, attr):
		self.name = name
		self.vaddr = vaddr
		self.vend = vend
		self.attr = attr
	
'''
######################################################################################

* ELF Header

#define EI_NIDENT	16

typedef struct { 
	unsigned char	e_ident[EI_NIDENT];
	Elf32_Half 		e_type;
	Elf32_Half 		e_machine;
	Elf32_Word 		e_version;
	Elf32_Addr 		e_entry;
	Elf32_Off 		e_phoff;
	Elf32_Off 		e_shoff;
	Elf32_Word 		e_flags;
	Elf32_Half 		e_ehsize;
	Elf32_Half 		e_phentsize;
	Elf32_Half 		e_phnum;
	Elf32_Half 		e_shentsize;
	Elf32_Half 		e_shnum;
	Elf32_Half		e_shstrndx;
} Elf32_Ehdr;
  
 ######################################################################################      
'''		
class ELF32Ehdr:
	def __init__(self, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstridx):
		self.e_entry = e_entry
		self.e_phoff = e_phoff
		self.e_shoff = e_shoff
		self.e_flags = e_flags
		self.e_ehsize = e_ehsize
		self.e_phentsize = e_phentsize
		self.e_phnum = e_phnum
		self.e_shentsize = e_shentsize
		self.e_shnum = e_shnum
		self.e_shstridx = e_shstridx
	def __str__(self):
		output = "  Entry point address:               %x\n" % self.e_entry
		output += "  Start of program headers:          %x (bytes into file)\n" % self.e_phoff
		output += "  Start of section headers:          %x (bytes into file)\n" % self.e_shoff
		output += "  Size of this header:               %x (bytes)\n" % self.e_ehsize
		output += "  Size of program headers:           %x (bytes)\n" % self.e_phentsize
		output += "  Number of program headers:         %x\n" % self.e_phnum
		output += "  Size of section headers:           %x (bytes)\n" % self.e_shentsize
		output += "  Number of section headers:         %x\n" % self.e_shnum
		output += "  Section header string table index: %x\n" % self.e_shstridx
		return output

'''
######################################################################################

* Program Header

typedef struct { 
	Elf32_Word		p_type;
	Elf32_Off 		p_offset;
	Elf32_Addr 		p_vaddr;
	Elf32_Addr 		p_paddr;
	Elf32_Word 		p_filesz;
	Elf32_Word 		p_memsz;
	Elf32_Word 		p_flags;
	Elf32_Word		p_align;
} Elf32_Phdr;

######################################################################################
'''
class ELF32Phdr:
	dict_p_type = {
	0: "NULL", 1: "LOAD", 2: "DYNAMIC", 3: "INTERP",
	4: "NOTE", 5: "SHLIB", 6: "PHDR", 7: "TLS",
	0x60000000: "LOOS", 0x6464e550: "UNWIND", 0x6474e550: "EH_FRAME", 
	0x6474e551: "GNU_STACK", 0x6474e552: "GNU_RELRO",
	0x6ffffffa: "LOSUNW", 0x6ffffffb: "STACK", 0x6ffffffc: "DTRACE",
	0x6ffffffd: "CAP", 0x6fffffff: "HIOS", 
	0x70000000: "LOPROC", 0x70000001: "EXIDX", 0x7fffffff: "HIPROC"
	}

	def __init__(self, p_type, p_offset, p_vaddr, p_filesz, p_memsz, p_flags, p_align):
		self.p_type   = p_type
		self.p_offset = p_offset
		self.p_vaddr  = p_vaddr
		self.p_filesz = p_filesz
		self.p_memsz  = p_memsz
		self.p_flags  = p_flags
		self.p_align  = p_align
	def type2str(self, type):
		return dict_search_safe(self.dict_p_type, type)
	def __str__(self):
		return "  %-16s %8x %8x %8x %8x %8x" % (self.type2str(self.p_type), self.p_offset, self.p_vaddr, self.p_filesz, self.p_memsz, self.p_flags)

class ELF32Shdr:
	dict_sh_type = {
	0: "NULL", 1: "PROGBITS", 2: "SYMTAB", 3: "STRTAB",
	4: "RELA", 5: "HASH", 6: "DYNAMIC",	7: "NOTE",
	8: "NOBITS", 9: "REL", 10: "SHLIB", 11: "DYNSYM",
	14: "INIT_ARRAY", 15: "FINI_ARRAY", 16: "PREINIT_ARRAY", 
	17: "GROUP", 18: "SYMTAB_SHNDX",
	0x60000000: "LOOS", 0x6fffffef: "LOSUNW", #0x6fffffef
	0x6ffffff0: "SUNW_capinfo", 0x6ffffff1: "SUNW_symsort", 0x6ffffff2: "SUNW_tlssort", 
	0x6ffffff3: "SUNW_LDYNSYM", 0x6ffffff4: "SUNW_dof", 0x6ffffff5: "SUNW_cap",
	0x6ffffff6: "SUNW_SIGNATURE", 0x6ffffff7: "SUNW_ANNOTATE", 0x6ffffff8: "SUNW_DEBUGSTR", 
	0x6ffffff9: "SUNW_DEBUG", 0x6ffffffa: "SUNW_move", 0x6ffffffb: "SUNW_COMDAT", 
	0x6ffffffc: "SUNW_syminfo", 0x6ffffffd: "SUNW_verdef", 0x6ffffffe: "VERNEED", 
	0x6fffffff: "VERSYM", 
	0x70000000: "LOPROC",  0x70000001: "ARM_EXIDX", 0x70000003: "ARM_ATTRIBUTES",0x7fffffff: "HIPROC", 
	0x80000000: "LOUSER", 0xffffffff: "HIUSER"
	}
#	def __init__(self, sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link, sh_info, sh_addralign, sh_entsize):
	def __init__(self, sh_name, sh_type, sh_offset, sh_size, sh_flags=0, sh_addr=0, sh_link=0, sh_info=0, sh_addralign=1, sh_entsize=0):
		self.sh_name = sh_name
		self.sh_type = sh_type
		self.sh_flags = sh_flags
		self.sh_addr = sh_addr
		self.sh_offset = sh_offset
		self.sh_size = sh_size
		self.sh_link = sh_link
		self.sh_info = sh_info
		self.sh_addralign = sh_addralign
		self.sh_entsize = sh_entsize
		# for fake section headers
		if isinstance(sh_name, str):
			self.name = sh_name

	def type2str(self, type):
		return dict_search_safe(self.dict_sh_type, type)
	def __str__(self):
		return "  %-24s %-16s %8x %8x %8x %8x" % (self.name, self.type2str(self.sh_type), self.sh_addr, self.sh_offset, self.sh_size, self.sh_entsize)

class ELFStrTab:
	def __init__(self, content):
		self.content = content
	def get_str(self, idx):
		end = self.content.index(chr(0), idx)
		return self.content[idx:end]#self.content.index(idx, chr(0))]

'''
######################################################################################
 
 * Symble Table

 typedef struct { 
 	Elf32_Word 		st_name;
 	Elf32_Addr 		st_value;
 	Elf32_Word		st_size;
	unsigned char 	st_info;
	unsigned char 	st_other;
	Elf32_Half		st_shndx;
} Elf32_Sym;

######################################################################################
'''
class ELF32SymTab:
	dict_st_bind = {
		0: "LOCAL",
		1: "GLOBAL",
		2: "WEAK",
		10: "LOOS",
		12: "HIOS",
		13: "LOPROC",
		15: "HIPROC"
		}
	dict_st_type = {
		0: "NOTYPE",
		1: "OBJECT",
		2: "FUNC",	# for FUN, st_value means func addr, st_size means code size
		3: "SECTION",
		4: "FILE",
		5: "COMMON",
		6: "TLS",
		10: "LOOS",
		12: "HIOS",
		13: "LOPROC",
		15: "HIPROC"
		}

	def __init__(self, content, strtab):
		self.strtab = strtab
		self.symbols = []
		for idx in range(0, len(content), 16):
			self.symbols.append(struct.unpack('<IIIbbH', content[idx:idx+16]))
	'''
	def type2str(self, type):
		return dict_search_safe(self.dict_dt_type, type)
	'''
	def get_id(self, id):
		(st_name, st_value, st_size, st_info, st_other, st_shndx) = self.symbols[id]
		return (self.strtab.get_str(st_name), st_value)

	def __str__(self):
		output = ""
		for i,it in enumerate(self.symbols):
			#print "  %8x %-24s %x" % (it[0], '('+self.type2str(it[0])+')', it[1])
			(st_name, st_value, st_size, st_info, st_other, st_shndx) = it
			st_bind = st_info >> 4
			st_type = st_info & 0xf 
			output += "%4d: %8x %8x %-10s %-10s %d %d %s\n" % (i, st_value, st_size, self.dict_st_type[st_type], 
				self.dict_st_bind[st_bind], st_other, st_shndx, self.strtab.get_str(st_name))
		return output

'''
######################################################################################

* Relocation Entries

 typedef struct {
      Elf32_Addr  r_offset;
      Elf32_Word  r_info;
 } Elf32_Rel;

######################################################################################
'''

class ELF32Rel:
	dict_rel_type = {
		22 : "R_ARM_JUMP_SLOT",
		21 : "R_ARM_GLOB_DAT",
		2 : "R_ARM_ABS32",
		3 : "R_ARM_REL32",
		23 : "R_ARM_RELATIE",
		20 : "R_ARM_COPY"
	}

	def __init__(self, content, dynsym):
		self.rels = []
		self.dynsym = dynsym
		for idx in range(0, len(content), 8):
			self.rels.append(struct.unpack('<II', content[idx:idx+8]))

	def type2str(self, type):
		return dict_search_safe(self.dict_rel_type, type)

	def __str__(self):
		output = ""
		for it in self.rels:
			(r_offset, r_info) = it
			r_type = r_info & 0xff 
			r_sym = r_info >> 8
			if r_sym:
				sym_name, sym_value = self.dynsym.get_id(r_sym)
				output += "%8x %6x,%02x %-20s %-8d %s\n" % (r_offset, r_sym, r_type, self.type2str(r_type), sym_value, sym_name)
			else:
				output += "%8x %6x,%02x %-20s\n" % (r_offset, r_sym, r_type, self.type2str(r_type))
		return output

'''
######################################################################################

* Dynamic Section Structure

 typedef struct {
     Elf32_Sword d_tag;
     union {
         Elf32_Word  d_val;
         Elf32_Addr  d_ptr;
     } d_un;
 } Elf32_Dyn;

######################################################################################
'''
class ELF32Dynamic:
	dict_dt_type = {
	1: "NEEDED",
	2: "PLTRELSZ",
	3: "PLTGOT",
	4: "HASH",
	5: "STRTAB",
	6: "SYMTAB",
	7: "RELA",
	12: "INIT",
	13: "FINI",
	16: "SYMBOLIC",
	17: "REL",
	18: "RELSZ",
	20: "PLTREL",
	21: "DEBUG",
	22: "TEXTREL",
	23: "JMPREL",
	25: "INIT_ARRAY",
	26: "FINI_ARRAY",
	27: "INIT_ARRAYSZ",
	28: "FINI_ARRAYSZ",
	30: "FLAGS",
	32: "PREINIT_ARRAY",
	33: "PREINIT_ARRAYSZ",

	0: "NULL",
	8: "RELASZ",
	9: "RELAENT",
	10: "STRSZ",
	11: "SYMENT",
	14: "SONAME",
	15: "RPATH",
	19: "RELENT",
	24: "BIND_NOW",
	29: "RUNPATH",
	32: "ENCODING",
	34: "MAXPOSTAGS",
	
	0x6000000d: "LOOS",	0x6ffff000: "HIOS",	0x6ffffd00: "VALRNGLO",	0x6ffffdf8: "CHECKSUM",
	0x6ffffdf9: "PLTPADSZ",	0x6ffffdfa: "MOVEENT",	0x6ffffdfb: "MOVESZ",	0x6ffffdfd: "POSFLAG_1",
	0x6ffffdfe: "SYMINSZ",	0x6ffffdff: "SYMINENT",	0x6ffffdff: "VALRNGHI",	0x6ffffe00: "ADDRRNGLO",
	0x6ffffef5: "GNU_HASH",	0x6ffffefa: "CONFIG",	0x6ffffefb: "DEPAUDIT",	0x6ffffefc: "AUDIT",
	0x6ffffefd: "PLTPAD",	0x6ffffefe: "MOVETAB",	0x6ffffeff: "SYMINFO",	0x6ffffeff: "ADDRRNGHI",
	0x6ffffff0: "VERSYM",	0x6ffffff9: "RELACOUNT",	0x6ffffffa: "RELCOUNT",	0x6ffffffb: "FLAGS_1",
	0x6ffffffc: "VERDEF",	0x6ffffffd: "VERDEFNUM",	0x6ffffffe: "VERNEED",	0x6fffffff: "VERNEEDNUM",
	0x70000000: "LOPROC",	0x70000001: "SPARC_REGISTER",	0x7ffffffd: "AUXILIARY",	0x7ffffffe: "USED",
	0x7fffffff: "FILTER",
	0x7fffffff: "HIPROC"
	}

	def __init__(self, content):
		self.dyns = []
		for idx in range(0, len(content), 8):
			self.dyns.append(struct.unpack('<II', content[idx:idx+8]))
	def get_by_tag(self, tag):
		#print "searching %s" % tag
		for it in self.dyns:
			(t, v) = it
			#print "  %d %d" % it
			if t == tag:
				return v
		return None
	def type2str(self, type):
		return dict_search_safe(self.dict_dt_type, type)
	def __str__(self):
		output = ""
		for it in self.dyns:
			output += "  %8x %-24s %x\n" % (it[0], '('+self.type2str(it[0])+')', it[1])
		return output

class ELFImage:
	def __init__(self, f):
		#self.fp = f
		self._opener(f)
		self.segments = self.sections = []
		self._parse_eheader()
		self._parse_pheader()
		try: 
			self._parse_sheader()
		except Exception as e:
			self.sections = []
			print "section header parse error"
			#print e
			traceback.print_exc()
			print "-" * 8

		#print len(self.sections), self.dynamic
		if not self.sections and self.dynamic:
			print "Warning: no section found, faking it"
			self._fake_sections()

		'''
		self.sections = []
		f.seek(self.loads[0].p_offset, 0)
		load0_data = f.read(self.loads[0].p_filesz)
		'''
		if self.static_compile:
			#self.add_static_compile()
			pass
		else:
			#self.add_dynamic_compile()
			#self.dump(4)
			pass

	def _opener(self, f):
		self.fp = open(f, "r")

	def _parse_eheader(self):
		# elf header
		self.fp.seek(16, 0)
		(e_type,   e_machine, e_version,  e_entry,  
		 e_phoff,  e_shoff,   e_flags,    e_ehsize, 
		 e_phentsize, e_phnum,  e_shentsize, 
		 e_shnum,  e_shstridx) = struct.unpack('<HHIIIIIHHHHHH', self.fp.read(36))
		self.ehdr = ELF32Ehdr(e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstridx)
	
	def _parse_pheader(self):
		# program header (segments)
		self.static_compile = True
		self.loads = []
		self.segments = []
		self.fp.seek(self.ehdr.e_phoff, 0)
		for i in range(self.ehdr.e_phnum):
			(p_type, p_offset, p_vaddr, p_paddr, 
			p_filesz, p_memsz, p_flags, p_align) = struct.unpack('<IIIIIIII', self.fp.read(32))
			phdr = ELF32Phdr(p_type, p_offset, p_vaddr, p_filesz, p_memsz, p_flags, p_align)
			self.segments.append(phdr)

			if p_type == PT_LOAD:
				self.loads.append(phdr)
			if p_type == PT_DYNAMIC:
				self.dynamic = phdr
				self.static_compile = False
			if p_type == 0x70000001:
				self.arm_exidx = phdr

		if len(self.loads) != 2:
			print('Program segment modifed file, no analysis now!')
			raise Exception("Program segment modifed file")

	def _parse_sheader(self):
		# Section header
		self.sections = []
		self.fp.seek(self.ehdr.e_shoff, 0)
		
		if self.ehdr.e_shnum == 0:
			return

		for i in range(self.ehdr.e_shnum):
			(sh_name, sh_type, sh_flags, sh_addr, sh_offset, 
			sh_size, sh_link, sh_info, sh_addralign, sh_entsize) = struct.unpack('<IIIIIIIIII', self.fp.read(40))
			# NOTE: ELF32Shdr paramter order changed, for convient of create new class
			shdr = ELF32Shdr(sh_name, sh_type, sh_offset, sh_size, sh_flags, sh_addr, sh_link, sh_info, sh_addralign, sh_entsize)
			self.sections.append(shdr)

		# get section names from shstrtab
		strtab = self.load_section(self.ehdr.e_shstridx)
		for i in self.sections:
			i.name = strtab.get_str(i.sh_name)

	def _fake_sections(self):
		if self.sections:
			raise Exception("sections not null, stop faking sections")
		
		# fake .dynamic section
		fake_dyn = ELF32Shdr(".dynamic", SHT_DYNAMIC, self.dynamic.p_offset, self.dynamic.p_filesz)
		#fake_dyn.name = ".dynamic"
		self.sections.append(fake_dyn)
		dyn = self.load_section(fake_dyn)

#		try:
		# fake .dynstr, .dynsym
		addr = dyn.get_by_tag(DT_STRTAB)
		size = dyn.get_by_tag(DT_STRSZ)
		print "%x %x"% (addr, size)
		self.sections.append(ELF32Shdr(".dynstr", SHT_STRTAB, addr, size))
		addr = dyn.get_by_tag(DT_SYMTAB)
		entsz = dyn.get_by_tag(DT_SYMENT)
		hash_addr = dyn.get_by_tag(DT_HASH)
		(nbucket, nchain) = struct.unpack('<II', self._read_bytes(hash_addr, 8))
		print addr, entsz, nbucket, nchain
		self.sections.append(ELF32Shdr(".dynsym", SHT_DYNSYM, addr, entsz*nchain))
		# TODO: fake .hash

		# fake .rel.dyn, .rel.plt
		self.sections.append(ELF32Shdr(".rel.dyn", SHT_REL, dyn.get_by_tag(DT_REL), dyn.get_by_tag(DT_RELSZ)))
		self.sections.append(ELF32Shdr(".rel.plt", SHT_REL, dyn.get_by_tag(DT_JMPREL), dyn.get_by_tag(DT_PLTRELSZ)))

		# fake .init.array, .fini.array
		self.sections.append(ELF32Shdr(".init.array", SHT_INIT_ARRAY, dyn.get_by_tag(DT_INIT_ARRAY), dyn.get_by_tag(DT_INIT_ARRAYSZ)))
		self.sections.append(ELF32Shdr(".fini.array", SHT_FINI_ARRAY, dyn.get_by_tag(DT_FINI_ARRAY), dyn.get_by_tag(DT_FINI_ARRAYSZ)))

		# TODO: fake .got
		# TODO: fake .plt

	def _read_bytes(self, off, size):
		self.fp.seek(off, 0)
		return self.fp.read(size)

	def get_section_hdr_by_type(self, type):
		return [x for x in self.sections if x.sh_type == type]

	def load_section(self, target):
		# return class ELF32Shdr by name
		def get_section_hdr(name):
			for sec in self.sections:
				if sec.name == name:
					return sec
			return None

		if isinstance(target, ELF32Shdr):
			#print "is section header"
			sec_hdr = target
		elif isinstance(target, int):
			sec_hdr = self.sections[target]
		elif isinstance(target, str):
			#print "is string"
			sec_hdr = get_section_hdr(target)

		content = self._read_bytes(sec_hdr.sh_offset, sec_hdr.sh_size)
		#stream = io.BytesIO(content)

		t = sec_hdr.sh_type
		if t == SHT_STRTAB:
			return ELFStrTab(content)
		elif t == SHT_DYNAMIC:
			return ELF32Dynamic(content)
		elif t == SHT_REL:
			return ELF32Rel(content, self.load_section(".dynsym")) 
		elif t == SHT_DYNSYM:
			return ELF32SymTab(content, self.load_section(".dynstr"))
		elif t == SHT_SYMTAB:
			# TODO: strtab & symtab
			pass
		else:
			raise Exception("Section parser Not implemented")
		#sec_hdr = get_section_hdr(name)

	def dump(self, type):
		if type == "h":	# ELF header
			print "ELF Header:"
			print self.ehdr
		elif type == "l":	# Program header
			print "Program Headers:"
			print "  Type               Offset  VirtAddr FileSiz   MemSiz      Flg"
			for phdr in self.segments:
				print phdr
		elif type == "S":	# Section header
			print "Section Headers:"
			print "  Name                     Type                 Addr      Off     Size  Entsize"
			for shdr in self.sections:
				print shdr

		elif type == "d": # Dynamic
			print "Dynamic section:"
			print self.load_section(".dynamic")
		elif type == "s": # Dynsym
			print "Dynamic Symbol:"
			print " Num:    Value     Size Type       Bind    Vis    Ndx Name"
			print self.load_section(".dynsym")
		elif type == "r": # relocation
			for rel in self.get_section_hdr_by_type(9):
				print "Relocation section '%s' at offset %x:" % (rel.name, rel.sh_offset)
				print "  Offset     Info    Type          Sym.Value   Sym.Name"
				print self.load_section(rel)	

	def add_static_compile(self):
		print('*** This file is statically compiled! ***')
		text_offset = 52 + (self.ehdr.e_phoff - 52) + self.ehdr.e_phnum * 32
		text_offset = (text_offset + 0xf) & ~0xf
		text_vaddr = text_offset + self.loads[0].p_vaddr
		
		end_tag = SearchTextEnd(load0_data)
		if end_tag != -1:
			self.sections.append(Section('.note.android.ident', self.loads[0].p_vaddr + end_tag, self.arm_exidx.p_vaddr, 'DATA'))
		self.sections.append(Section('.text', text_vaddr, self.loads[0].p_vaddr + end_tag, 'CODE'))
		self.sections.append(Section('.arm.exidx', self.arm_exidx.p_vaddr, self.arm_exidx.p_vaddr + self.arm_exidx.p_filesz, 'DATA'))				
			
		[rodata_offset, rodata_len] = SearchRODATA(load0_data, self.arm_exidx.p_offset + self.arm_exidx.p_filesz, self.loads[0].p_offset + self.loads[0].p_filesz)
		if rodata_offset != -1:
			rodata_vaddr = rodata_offset + self.loads[0].p_vaddr
			self.sections.append(Section('.arm.extab',  self.arm_exidx.p_vaddr + self.arm_exidx.p_filesz, rodata_vaddr, 'DATA'))
		else:
			rodata_vaddr = self.arm_exidx.p_vaddr + self.arm_exidx.p_filesz
		self.sections.append(Section('.rodata', rodata_vaddr, self.loads[0].p_vaddr + self.loads[0].p_filesz, 'DATA'))
		self.sections.append(Section('.data', self.loads[1].p_vaddr, self.loads[1].p_vaddr + self.loads[1].p_filesz, 'DATA'))
		self.sections.append(Section('.bss', self.loads[1].p_vaddr + self.loads[1].p_filesz, self.loads[1].p_vaddr + self.loads[1].p_memsz, 'DATA'))

	def add_dynamic_compile(self):
		print "%x" % self.dynamic.p_offset
		f.seek(self.dynamic.p_offset, 0)
		for i in range(self.dynamic.p_filesz / 8):
			(d_tag, d_val) = struct.unpack('<II', f.read(8))
			if d_tag == DT_SYMTAB:
				symtab_vaddr = d_val
			elif d_tag == DT_STRTAB:
				strtab_vaddr = d_val
			elif d_tag == DT_STRSZ:
				strtabSize = d_val
			elif d_tag == DT_HASH:
				hashtab_vaddr = d_val
			elif d_tag == DT_INIT_ARRAY:
				initArray_vaddr = d_val
			elif d_tag == DT_INIT_ARRAYSZ:
				initArraySize = d_val
			elif d_tag == DT_FINI_ARRAY:
				finiArray_vaddr = d_val
			elif d_tag == DT_FINI_ARRAYSZ:
				finiArraySize = d_val
			elif d_tag == DT_PREINIT_ARRAY:
				preinitArray_vaddr = d_val
			elif d_tag == DT_PREINIT_ARRAYSZ:
				preinitArraySize = d_val
			elif d_tag == DT_REL:
				rel_vaddr = d_val
			elif d_tag == DT_RELSZ:
				relSize = d_val
			elif d_tag == DT_JMPREL:
				relPlt_vaddr = d_val
			elif d_tag == DT_PLTRELSZ:
				relPltSize = d_val
			else:
				pass
		f.seek(hashtab_vaddr - self.loads[0].p_vaddr, 0)
		[nbucket, nchain] = struct.unpack('<II', f.read(8))
		f.seek(symtab_vaddr - self.loads[0].p_vaddr, 0)
		symtab = f.read(nchain * 16)
		
		f.seek(strtab_vaddr - self.loads[0].p_vaddr, 0)
		strtab = f.read(strtabSize)
		
		f.seek(rel_vaddr - self.loads[0].p_vaddr, 0)
		rel = f.read(relSize)
		
		f.seek(relPlt_vaddr - self.loads[0].p_vaddr, 0)
		relPlt = f.read(relPltSize)
					
		f.seek(initArray_vaddr - self.loads[1].p_vaddr, 0)
		initArray = f.read(initArraySize)

		f.seek(finiArray_vaddr - self.loads[1].p_vaddr, 0)
		finiArray = f.read(finiArraySize)
		
		f.seek(preinitArray_vaddr - self.loads[1].p_vaddr, 0)
		preinitArray = f.read(preinitArraySize)			
		#
		plt_offset = SearchPltStart(load0_data)
		self.sections.append(Section('.plt', plt_offset + self.loads[0].p_vaddr, plt_offset + self.loads[0].p_vaddr + 20 + 12 * relPltSize / 8, 'CODE'))
		
		text_offset = plt_offset + 20 + 12 * relPltSize / 8
		text_vaddr = self.loads[0].p_vaddr + text_offset
		end_tag = SearchTextEnd(load0_data)
		
		if end_tag != -1:
			self.sections.append(Section('.note.android.ident', self.loads[0].p_vaddr + end_tag, self.arm_exidx.p_vaddr, 'DATA'))
		self.sections.append(Section('.text', text_vaddr, self.loads[0].p_vaddr + end_tag, 'CODE'))
		self.sections.append(Section('.arm.exidx', self.arm_exidx.p_vaddr, self.arm_exidx.p_vaddr + self.arm_exidx.p_filesz, 'DATA'))				
		
		[rodata_offset, rodata_len] = SearchRODATA(load0_data, self.arm_exidx.p_offset + self.arm_exidx.p_filesz, self.loads[0].p_offset + self.loads[0].p_filesz)
		if rodata_offset != -1:
			rodata_vaddr = rodata_offset + self.loads[0].p_vaddr
			self.sections.append(Section('.arm.extab',  self.arm_exidx.p_vaddr + self.arm_exidx.p_filesz, rodata_vaddr, 'DATA'))
		else:
			rodata_vaddr = self.arm_exidx.p_vaddr + self.arm_exidx.p_filesz
		self.sections.append(Section('.rodata', rodata_vaddr, self.loads[0].p_vaddr + self.loads[0].p_filesz, 'DATA'))	
		self.sections.append(Section('.init_array', initArray_vaddr, initArray_vaddr + initArraySize, 'DATA'))
		self.sections.append(Section('.fini_array', finiArray_vaddr, finiArray_vaddr + finiArraySize, 'DATA'))
		self.sections.append(Section('.preinit_array', preinitArray_vaddr, preinitArray_vaddr + preinitArraySize, 'DATA'))
		
		self.rels = []			
		for i in range(0, relPltSize, 8):
			[r_offset, r_info] = struct.unpack('<II', relPlt[i: i+8])
			sym_index = r_info >> 8
			[st_name, st_value] = struct.unpack('<II', symtab[sym_index * 16: sym_index * 16 + 8])
			tail = findCstringTail(strtab[st_name : len(strtab)])
			st_name = strtab[st_name: st_name + tail]
			self.rels.append(RelInfo(st_name, r_offset, True))				
		
		f.seek(self.loads[1].p_offset, 0)
		load1_data = f.read(self.loads[1].p_filesz)
		got_end_offset = SearchGotEnd(load1_data, preinitArray_vaddr + preinitArraySize - self.loads[1].p_vaddr, self.loads[1].p_filesz, self.rels)
		if got_end_offset == 0:
			self.sections.append(Section('.got', preinitArray_vaddr + preinitArraySize, self.loads[1].p_vaddr + self.loads[1].p_filesz, 'DATA'))
		else:
			self.sections.append(Section('.got', preinitArray_vaddr + preinitArraySize, self.loads[1].p_vaddr + got_end_offset, 'DATA'))
			self.sections.append(Section('.data', preinitArray_vaddr + preinitArraySize, self.loads[1].p_vaddr + got_end_offset, 'DATA'))
		self.sections.append(Section('.bss', self.loads[1].p_vaddr + self.loads[1].p_filesz, self.loads[1].p_vaddr + self.loads[1].p_memsz, 'DATA'))

def findCstringTail(str):
	retval = -1

	for i in range(0, len(str)):
		if str[i] == '\x00':
			retval = i
			break
	return retval


def load_file(f, neflags, format):
	#print('------------Log begin ---------------')
	#f.seek(0)
	elf = ELFImage(f)
	'''
	idaapi.set_processor_type("arm", SETPROC_ALL|SETPROC_FATAL)
	
	for i in range(len(elf.loads)):
		f.file2base(elf.loads[i].p_offset, elf.loads[i].p_vaddr, elf.loads[i].p_vaddr + elf.loads[i].p_filesz, 1)
		if len(elf.loads) != 2:
			if elf.loads[i].p_flags & 0x1 == 1:
				add_segm(0, elf.loads[i].p_vaddr, elf.loads[i].p_vaddr + elf.loads[i].p_filesz, ('load%d' %i), 'CODE')
			else:
				add_segm(0, elf.loads[i].p_vaddr, elf.loads[i].p_vaddr + elf.loads[i].p_filesz, ('load%d' %i), 'DATA')
	if elf.ehdr.e_entry % 2 == 1:
		add_entry(elf.ehdr.e_entry & ~(0x1), elf.ehdr.e_entry & ~(0x1), 'start', 0)
	else:
		add_entry(elf.ehdr.e_entry, elf.ehdr.e_entry, 'start', 1)	
	
	if len(elf.loads) != 2:
		return 1
	for i in range(len(elf.sections)):
		add_segm(0, elf.sections[i].vaddr, elf.sections[i].vend, elf.sections[i].name, elf.sections[i].attr)
	
	if not elf.static_compile:
		extern_vaddr = elf.loads[1].p_vaddr + elf.loads[1].p_memsz
		add_segm(0, extern_vaddr, extern_vaddr + len(elf.rels) * 4, 'extern', 'XTRN')

		for i in range(len(elf.rels)):
			MakeDword(extern_vaddr + i * 4)
			MakeName(extern_vaddr + i * 4, '__imp_' + elf.rels[i].name)
			MakeName(elf.rels[i].r_offset, elf.rels[i].name + '_ptr')
			PatchDword(elf.rels[i].r_offset, extern_vaddr + i * 4)
	
	print('------------Log end ---------------')
	return 1
	'''
	return elf

class ELFWriter(ELFImage):
	def _opener(self, f):
		self.fp = open(f, "r+")

	def _write_eheader(self, ehdr):
		# elf header
		self.fp.seek(16, 0)
		output = struct.pack('<HHIIIIIHHHHHH', 3,  40, 1, ehdr.e_entry,  \
		 ehdr.e_phoff,  ehdr.e_shoff,   ehdr.e_flags,    ehdr.e_ehsize, \
		 ehdr.e_phentsize, ehdr.e_phnum,  ehdr.e_shentsize, \
		 ehdr.e_shnum,  ehdr.e_shstridx)
		#print "header len:", len(output)
		print "write ELF header ..."
		self.fp.write(output)

	def _write_pheader(self):
		# program header (segments)
#		self.static_compile = True
#		self.loads = []
#		self.segments = []

		self.fp.seek(self.ehdr.e_phoff, 0)
		for i,phdr in enumerate(self.segments):
			print "write Program headers %d ..." % i
			# use p_vaddr as p_paddr, they are always same
			output = struct.pack('<IIIIIIII', phdr.p_type, phdr.p_offset, phdr.p_vaddr, phdr.p_vaddr, \
				phdr.p_filesz, phdr.p_memsz, phdr.p_flags, phdr.p_align)
			self.fp.write(output)


class MMFixer(ELFWriter):
	def fix_eheader(self):
		self.ehdr.e_shoff = 0
		self.ehdr.e_shentsize = 0
		self.ehdr.e_shnum = 0
		self.ehdr.e_shstridx = 0
		self._write_eheader(self.ehdr)

	def fix_pheader(self):
		# 0 LOAD .TEXT
		p = self.segments[0]
		p.p_filesz = p.p_memsz

		# 1 LOAD .DATA
		p = self.segments[1]
		p.p_offset = p.p_vaddr

		# 2 DYNAMIC .DYNAMIC
		p = self.segments[2]
		p.p_offset = p.p_vaddr

		self._write_pheader()


import sys, os
def patch_elf(orig):
	path,ext = os.path.splitext(orig)
	dest = path+"_r1"+ext

	print "Patch %s to %s" % (orig, dest)
	os.system("cp " + orig + " " + dest)

	m = MMFixer(dest)
	# R1
	m.fix_eheader()
	m.fix_pheader()
	# R2

if __name__ == "__main__":
	default_target = "/Users/cpeng/Downloads/mm352/dump/libaspirecommon.so"
	targets, options = [],[]
	for t in sys.argv[1:]:
		if t[0] == '-':
			options.append(t[1:])
		else:
			targets.append(t)

	if not targets:	targets= [default_target]
	if not options: options = ['h', 'l', 'S']

	# if modification flag exist
	if 'f' in options:
		options.remove('f')
		patch_elf(targets[0])
		sys.exit(0)	

	for t in targets:
		if len(targets) > 1: print "File:", t
		e = ELFImage(t)
		for opt in options:
			e.dump(opt)
		#print e, e.loads

