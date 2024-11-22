import docker
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import json

logger = logging.getLogger(__name__)

class ProgrammingEnvironment:
    """Base class for programming environments"""
    def __init__(self, language: str, workspace_name: str):
        self.language = language
        self.workspace_name = workspace_name
        self.docker_client = docker.from_env()
        self.container = None
        self.workspace_path = Path(f"workspaces/programming/{language}/{workspace_name}")
        
    def setup_base_environment(self) -> bool:
        """Set up base programming environment"""
        try:
            os.makedirs(self.workspace_path / "src", exist_ok=True)
            os.makedirs(self.workspace_path / "tests", exist_ok=True)
            os.makedirs(self.workspace_path / "build", exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to setup base environment: {e}")
            return False
            
    def cleanup(self):
        """Clean up environment"""
        try:
            if self.container:
                self.container.stop()
                self.container.remove()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


class PythonLab(ProgrammingEnvironment):
    """Python development environment"""
    def __init__(self, workspace_name: str):
        super().__init__("python", workspace_name)
        
    def setup_environment(self) -> bool:
        """Set up Python development environment"""
        try:
            self.setup_base_environment()
            
            # Start Python container
            self.container = self.docker_client.containers.run(
                "python:3.10-slim",
                detach=True,
                volumes={
                    str(self.workspace_path.absolute()): {
                        'bind': '/workspace',
                        'mode': 'rw'
                    }
                },
                working_dir="/workspace",
                command="sleep infinity"
            )
            
            # Install development tools
            self.container.exec_run("pip install pytest black mypy pylint")
            
            return True
        except Exception as e:
            logger.error(f"Failed to setup Python environment: {e}")
            return False
            
    def run_tests(self, test_file: str) -> Dict:
        """Run Python tests"""
        try:
            result = self.container.exec_run(f"pytest {test_file} -v")
            return {'output': result.output.decode()}
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return {'error': str(e)}
            
    def lint_code(self, source_file: str) -> Dict:
        """Lint Python code"""
        results = {}
        try:
            # Run pylint
            pylint_result = self.container.exec_run(f"pylint {source_file}")
            results['pylint'] = pylint_result.output.decode()
            
            # Run black
            black_result = self.container.exec_run(f"black --check {source_file}")
            results['black'] = black_result.output.decode()
            
            # Run mypy
            mypy_result = self.container.exec_run(f"mypy {source_file}")
            results['mypy'] = mypy_result.output.decode()
            
        except Exception as e:
            logger.error(f"Failed to lint code: {e}")
            results['error'] = str(e)
            
        return results


class CPPLab(ProgrammingEnvironment):
    """C++ development environment"""
    def __init__(self, workspace_name: str):
        super().__init__("cpp", workspace_name)
        
    def setup_environment(self) -> bool:
        """Set up C++ development environment"""
        try:
            self.setup_base_environment()
            
            # Start C++ container
            self.container = self.docker_client.containers.run(
                "gcc:latest",
                detach=True,
                volumes={
                    str(self.workspace_path.absolute()): {
                        'bind': '/workspace',
                        'mode': 'rw'
                    }
                },
                working_dir="/workspace",
                command="sleep infinity"
            )
            
            # Install development tools
            self.container.exec_run("apt-get update && apt-get install -y cmake clang-format cppcheck gdb valgrind")
            
            return True
        except Exception as e:
            logger.error(f"Failed to setup C++ environment: {e}")
            return False
            
    def build_project(self, build_type: str = "Debug") -> Dict:
        """Build C++ project"""
        try:
            cmds = [
                "cd build",
                "cmake ..",
                f"cmake --build . --config {build_type}"
            ]
            result = self.container.exec_run(" && ".join(cmds))
            return {'output': result.output.decode()}
        except Exception as e:
            logger.error(f"Failed to build project: {e}")
            return {'error': str(e)}
            
    def run_tests(self) -> Dict:
        """Run C++ tests"""
        try:
            result = self.container.exec_run("cd build && ctest --output-on-failure")
            return {'output': result.output.decode()}
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return {'error': str(e)}
            
    def analyze_code(self, source_file: str) -> Dict:
        """Analyze C++ code"""
        results = {}
        try:
            # Run clang-format
            format_result = self.container.exec_run(f"clang-format --style=llvm {source_file}")
            results['formatting'] = format_result.output.decode()
            
            # Run cppcheck
            check_result = self.container.exec_run(f"cppcheck --enable=all {source_file}")
            results['static_analysis'] = check_result.output.decode()
            
            # Run valgrind if executable exists
            if (self.workspace_path / "build" / "main").exists():
                valgrind_result = self.container.exec_run(
                    "valgrind --leak-check=full ./build/main"
                )
                results['memory_check'] = valgrind_result.output.decode()
                
        except Exception as e:
            logger.error(f"Failed to analyze code: {e}")
            results['error'] = str(e)
            
        return results


class CSharpLab(ProgrammingEnvironment):
    """C# development environment"""
    def __init__(self, workspace_name: str):
        super().__init__("csharp", workspace_name)
        
    def setup_environment(self) -> bool:
        """Set up C# development environment"""
        try:
            self.setup_base_environment()
            
            # Start .NET container
            self.container = self.docker_client.containers.run(
                "mcr.microsoft.com/dotnet/sdk:6.0",
                detach=True,
                volumes={
                    str(self.workspace_path.absolute()): {
                        'bind': '/workspace',
                        'mode': 'rw'
                    }
                },
                working_dir="/workspace",
                command="sleep infinity"
            )
            
            # Create new solution
            self.container.exec_run("dotnet new sln")
            
            return True
        except Exception as e:
            logger.error(f"Failed to setup C# environment: {e}")
            return False
            
    def create_project(self, project_type: str, name: str) -> bool:
        """Create new C# project"""
        try:
            # Create project
            self.container.exec_run(f"dotnet new {project_type} -n {name}")
            
            # Add to solution
            self.container.exec_run(f"dotnet sln add {name}/{name}.csproj")
            
            return True
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            return False
            
    def build_solution(self, configuration: str = "Debug") -> Dict:
        """Build C# solution"""
        try:
            result = self.container.exec_run(f"dotnet build -c {configuration}")
            return {'output': result.output.decode()}
        except Exception as e:
            logger.error(f"Failed to build solution: {e}")
            return {'error': str(e)}
            
    def run_tests(self) -> Dict:
        """Run C# tests"""
        try:
            result = self.container.exec_run("dotnet test")
            return {'output': result.output.decode()}
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return {'error': str(e)}


class CLab(ProgrammingEnvironment):
    """C development environment"""
    def __init__(self, workspace_name: str):
        super().__init__("c", workspace_name)
        
    def setup_environment(self) -> bool:
        """Set up C development environment"""
        try:
            self.setup_base_environment()
            
            # Start C container
            self.container = self.docker_client.containers.run(
                "gcc:latest",
                detach=True,
                volumes={
                    str(self.workspace_path.absolute()): {
                        'bind': '/workspace',
                        'mode': 'rw'
                    }
                },
                working_dir="/workspace",
                command="sleep infinity"
            )
            
            # Install development tools
            self.container.exec_run(
                "apt-get update && apt-get install -y make cmake gdb valgrind clang-format"
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to setup C environment: {e}")
            return False
            
    def compile_program(self, source_file: str, output_file: str) -> Dict:
        """Compile C program"""
        try:
            result = self.container.exec_run(
                f"gcc -Wall -Wextra -g {source_file} -o {output_file}"
            )
            return {'output': result.output.decode()}
        except Exception as e:
            logger.error(f"Failed to compile program: {e}")
            return {'error': str(e)}
            
    def debug_program(self, program: str) -> Dict:
        """Debug C program using GDB"""
        try:
            result = self.container.exec_run(f"gdb {program}")
            return {'output': result.output.decode()}
        except Exception as e:
            logger.error(f"Failed to debug program: {e}")
            return {'error': str(e)}
            
    def memory_check(self, program: str) -> Dict:
        """Check for memory leaks using Valgrind"""
        try:
            result = self.container.exec_run(
                f"valgrind --leak-check=full --show-leak-kinds=all {program}"
            )
            return {'output': result.output.decode()}
        except Exception as e:
            logger.error(f"Failed to check memory: {e}")
            return {'error': str(e)}
