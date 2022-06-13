# TODO: reduce code duplication

TEST01_APK := tests/test01/app/build/outputs/apk/debug/app-debug.apk
TEST02_APK := tests/test02/app/build/outputs/apk/debug/app-debug.apk

build-test01:
	cd tests/test01; ./gradlew assembleDebug

build-test02:
	cd tests/test02; ./gradlew assembleDebug

test-test01: build-test01
	mkdir -p /tmp/test01.facts
	./build-run-markii.sh $(TEST01_APK) /tmp/test01.facts
	python3 tests/compare_facts.py /tmp/test01.facts tests/test01.facts

test-test02: build-test02
	mkdir -p /tmp/test02.facts
	./build-run-markii.sh $(TEST02_APK) /tmp/test02.facts
	python3 tests/compare_facts.py /tmp/test02.facts tests/test02.facts

# The APK is built from tempodroid/tree/c647d51/case-studies/ValidRec
test-validrec:
	mkdir -p /tmp/validrec.facts
	API_SEMANTICS_CONFIG=tests/recorder.yaml ./build-run-markii.sh tests/validrec/app-debug.apk /tmp/validrec.facts
	python3 tests/compare_facts.py /tmp/validrec.facts tests/validrec.facts

test-invalidrec:
	mkdir -p /tmp/invalidrec.facts
	API_SEMANTICS_CONFIG=tests/recorder.yaml ./build-run-markii.sh tests/invalidrec/app-debug.apk /tmp/invalidrec.facts
	python3 tests/compare_facts.py /tmp/invalidrec.facts tests/invalidrec.facts

test-all: test-test01 test-test02 test-validrec test-invalidrec

record-test01: build-test01
	rm -rf tests/test01.facts
	./build-run-markii.sh $(TEST01_APK) tests/test01.facts

record-test02: build-test02
	rm -rf tests/test02.facts
	./build-run-markii.sh $(TEST02_APK) tests/test02.facts

record-validrec:
	rm -rf tests/validrec.facts
	API_SEMANTICS_CONFIG=tests/recorder.yaml ./build-run-markii.sh tests/validrec/app-debug.apk tests/validrec.facts

record-invalidrec:
	rm -rf tests/invalidrec.facts
	API_SEMANTICS_CONFIG=tests/recorder.yaml ./build-run-markii.sh tests/invalidrec/app-debug.apk tests/invalidrec.facts

record-all: record-test01 record-test02 record-validrec record-invalidrec

update-testBasic-apk: build-test01 build-test02
	cp $(TEST01_APK) src/test/resources/testBasic/app-debug.apk
	@echo "TODO: manually copy over res and manifest from first step"

JAVA_FILES := $(shell find src -name "*.java")
SCALA_FILES := $(shell find src -name "*.scala")

JARFILE := target/scala-2.13/markii-assembly-0.1.jar

$(JARFILE): $(JAVA_FILES) $(SCALA_FILES)
	sbt assembly

jar: $(JARFILE)
